const chromium = require('chrome-aws-lambda');

exports.lambda_handler = async (event, context) => {
  let result = null;
  let browser = null;
  let query = event.query || 'twitter';

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

    return result
    // console.log(company_about);
    // console.log(company_page_url)

  } catch (error) {
    console.log(error)
  } finally {
    if (browser !== null) {
      await browser.close();
    }
  }

  return result;
};
