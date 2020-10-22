import json


def lambda_handler(event, context):
    company_domain = event["queryStringParameters"]["domain"]

    return _response(200, {"domain": company_domain})


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(payload),
    }
