import os
import json
import boto3
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from datastore import DataStore

SOURCE_DOMAIN = "crunchbase.com"


def lambda_handler(event, context):
    # print(json.dumps(event))
    query_domain = event.get("domain", "twitter.com")
    query = query_domain.split(".")[0].strip()
    url_session = "https://www.crunchbase.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
    }

    headers_xhr = dict(headers)
    headers_xhr.update(
        {"referer": "https://www.crunchbase.com/", "x-requested-with": "XMLHttpRequest"}
    )

    rq_sesion = requests.Session()

    rq_sesion.get(url_session, headers=headers)

    url_search_xhr = "https://www.crunchbase.com/v4/data/autocompletes?query={company}&collection_ids=organizations&limit=1&source=topSearch".format(
        company=query
    )
    # pdb.set_trace()
    res = rq_sesion.get(url_search_xhr, headers=headers_xhr)

    # print(res)
    company_slug = res.json()["entities"][0]["identifier"]["permalink"]
    url_crunchbase_company = "https://www.crunchbase.com/organization/" + company_slug

    res_company_summary = rq_sesion.get(url_crunchbase_company, headers=headers)
    soup = BeautifulSoup(res_company_summary.content, "lxml")

    company_about = soup.find(
        "description-card", class_="ng-star-inserted"
    ).text.strip()
    # company_location = soup.find(
    #     "identifier-multi-formatter", class_="ng-star-inserted"
    # ).text
    # for string in soup.find('fields-card', class_='ng-star-inserted').stripped_strings:print(string)
    soup.find("fields-card", class_="ng-star-inserted").find("ul").find_all("li")

    about_elements = (
        soup.find("fields-card", class_="ng-star-inserted").find("ul").find_all("li")
    )
    # pdb.set_trace()

    # assert len(about_elements) > 0, "UnMappable About elements!"
    (
        company_location,
        company_size,
        company_funding_round,
        company_ipo_status,
        company_website,
        company_rank,
    ) = (
        "",
        "",
        "",
        "",
        "",
        "",
    )

    for about_element in about_elements:
        element_href = []
        element_target = ""
        element_content = about_element.text.strip()
        if about_element.find("a"):
            element_href = about_element.find("a").get("href")
            element_target = about_element.find("a").get("target")
        if "num_employees_enum" in element_href:
            company_size = element_content
        if "location_group_identifiers" in element_href:
            company_location = element_content
        if "last_funding_type" in element_href:
            company_funding_round = element_content
        if "Private" in element_content:
            company_ipo_status = element_content
        if "Public" in element_content:
            company_ipo_status = element_content
        if element_target == "_blank":
            company_website = element_content.split("/")[0].strip()
        if "rank_org_company" in element_href:
            company_rank = int("".join(element_content.split(",")))

    highlight_elements = soup.find_all("mat-card")[1].find_all("a")
    # assert len(highlight_elements) > 0, "UnMappable Highlight elements"

    (
        company_stock_symbol,
        company_accusitions,
        company_funding_total,
        company_team_member_count,
        company_investor_count,
    ) = (
        "",
        "",
        "",
        "",
        "",
    )
    for element in highlight_elements:
        if "Stock" in element.find("label-with-info").text:
            company_stock_symbol = element.find("field-formatter").text.strip()
        if "Total Funding" in element.find("label-with-info").text:
            company_funding_total = element.find("field-formatter").text.strip()
        if "Acquisitions" in element.find("label-with-info").text:
            company_accusitions = int(element.find("field-formatter").text.strip())
        if "Current Team" in element.find("label-with-info").text:
            company_team_member_count = int(
                "".join(element.find("field-formatter").text.strip().split(","))
            )
        if "Investors" in element.find("label-with-info").text:
            company_investor_count = int(
                "".join(element.find("field-formatter").text.strip().split(","))
            )

    company_dict = {
        "company_about": company_about,
        "company_location": company_location,
        "company_size": company_size,
        "company_funding_round": company_funding_round,
        "company_ipo_status": company_ipo_status,
        "company_website": company_website,
        "company_rank": company_rank,
        "company_stock_symbol": company_stock_symbol,
        "company_accusitions": company_accusitions,
        "company_funding_total": company_funding_total,
        "company_team_member_count": company_team_member_count,
        "company_investor_count": company_investor_count,
    }
    table = DataStore.get_table_client()
    PK, SK = DataStore.profile_keys(domain=query_domain)
    item = dict()
    item[SOURCE_DOMAIN] = company_dict
    item["updated_at"] = DataStore.date_time_now()
    item["PK"] = PK
    item["SK"] = SK
    # print(json.dumps(item))

    data = table.get_item(Key={"PK": PK, "SK": SK})
    if not data.get("Item"):
        table.put_item(Item=item)
        _dump_to_s3(item[SOURCE_DOMAIN], query_domain)
    else:
        item_ = data["Item"]
        item_[SOURCE_DOMAIN] = company_dict
        item_["updated_at"] = DataStore.date_time_now()
        table.put_item(Item=item_)
        _dump_to_s3(item_[SOURCE_DOMAIN], query_domain)


def _dump_to_s3(json_data: dict, domain):
    bucket_name = os.getenv("BUCKET_NAME")
    date_str = _date_now()
    s3 = boto3.resource("s3")
    s3object = s3.Object(
        bucket_name, SOURCE_DOMAIN + "/" + date_str + "/" + domain + ".json"
    )

    s3object.put(Body=(bytes(json.dumps(json_data).encode("UTF-8"))))


def _date_now():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")
