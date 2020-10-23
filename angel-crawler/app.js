const chromium = require('chrome-aws-lambda');
const AWS = require('aws-sdk')

exports.lambda_handler = async (event, context) => {
  let result = null;
  let browser = null;
  let query_domain = event.domain || 'twitter.com';
  const query = query_domain.split('.')[0]
  try {
    browser = await chromium.puppeteer.launch({
      args: chromium.args,
      defaultViewport: chromium.defaultViewport,
      executablePath: await chromium.executablePath,
      headless: chromium.headless,
      ignoreHTTPSErrors: true,
    });

    let page = await browser.newPage();

    await page.goto('https://angel.co');
    // await page.click('#search');
    // await page.waitForSelector('input[aria-label="Search AngelList"]',{visible: true});
    // await page.type('input[aria-label="Search AngelList"]', query,{delay: 250});
    let query_results = await page.evaluate(async ({query}) => {
      let search_url = 'https://angel.co/autocomplete/search.json?query=' + query;
      console.log(search_url);
      const response = await fetch(search_url);
      const text = await response.text();
      return JSON.parse(text);
    }, {
      query
    });

    // console.log(query_results.results);
    let company_page_url = query_results.results[0]["url"]
    await page.goto(company_page_url)
    const result = await page.evaluate(() => {
      let about_text = document.querySelector("h3").innerText;
      const aside_elements = document.querySelector("aside").querySelector("dl")
      const aside_elements_dd_arr = aside_elements.querySelectorAll('dd')
      const aside_elements_dt_arr = aside_elements.querySelectorAll('dt')

      let [company_links, company_location, company_size, company_funding_total, company_market_tags, ] = [
        [],
        "",
        "",
        "",
        [],
      ]
      for (const [index, element] of aside_elements_dd_arr.entries()) {
        if (element.innerText.includes("Website"))
          aside_elements_dt_arr[index].querySelectorAll("a").forEach(a => company_links.push(a.href))


        if (element.innerText.includes("Location"))
          company_location = aside_elements_dt_arr[index].innerText
        if (element.innerText.includes("Company size"))
          company_size = aside_elements_dt_arr[index].innerText
        if (element.innerText.includes("Total raised"))
          company_funding_total = aside_elements_dt_arr[index].innerText


        if (element.innerText.includes("Markets"))
          aside_elements_dt_arr[index].querySelectorAll("a").forEach(a => company_market_tags.push(a.innerText))
      }
      return {
        "company_about": about_text,
        "company_links": company_links,
        "company_size": company_size,
        "company_funding_total": company_funding_total,
        "company_market_tags": company_market_tags,
      }
    })

    const docClient = new AWS.DynamoDB.DocumentClient()
    let [PK, SK] = ["Company" + "#" + query_domain, 'profile']
    const item = {
      'angel.co': result,
      'PK': PK,
      'SK': SK,
      'updated_at': new Date().toISOString()
    }
    const get_params = {
      TableName: process.env.TABLE_NAME,
      Key: {
        "PK": PK,
        "SK": SK
      }
    }
    const put_params = {
      TableName: process.env.TABLE_NAME,
      Item: item
    }
    const data = await getData(docClient, get_params)
    if (!data['Item']) {
      await insertData(docClient, put_params)
    } else {
      let item_ = data['Item']
      item_['angel.co'] = result
      item_["updated_at"] = new Date().toISOString()
      put_params['Item'] = item_
      await insertData(docClient, put_params)

    }


    // if not data.get("Item"):
    //     table.put_item(Item=item)
    // else:
    //     item_ = data["Item"]
    //     item_["crunchbase.com"] = company_dict
    //     item_["updated_at"] = DataStore.date_time_now()
    //     table.put_item(Item=item_)

  } catch (error) {
    console.log(error)
  } finally {
    if (browser !== null) {
      await browser.close();
    }
  }

  return result;
};


function getData(docClient, params) {
  console.log(params)
  return new Promise((resolve, reject) => {
    docClient.get(params, (err, data) => {
      if (err) {
        console.log("Unable to read items. Error: ", err)
        reject(err)
      } else {
        console.log("Successfully retrieved items. Error: ", JSON.stringify(data, null, 2))
        resolve(data)
      }
    })
  })
}

function insertData(docClient, params) {
  return new Promise((resolve, reject) => {
    docClient.put(params, (err, data) => {
      if (err) {
        console.log("Unable to write items. Error: ", err)
        reject(err)
      } else {
        console.log("Successfully added items. Error: ", JSON.stringify(data, null, 2))
        resolve(data)
      }
    })
  })
}