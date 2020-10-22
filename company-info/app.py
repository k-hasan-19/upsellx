import os
import json
import boto3
from botocore.exceptions import ClientError
from encoder_class import DecimalEncoder
from datastore import DataStore


def lambda_handler(event, context):
    company_domain = event["queryStringParameters"]["domain"]
    table = DataStore.get_table_client()
    PK, SK = DataStore.profile_keys(domain=company_domain)
    print("Key: ", json.dumps({"PK": PK, "SK": SK}, indent=4))

    try:
        data = table.get_item(Key={"PK": PK, "SK": SK})
        if not data.get("Item"):
            raise KeyError
        # response = table.get_item(Key={"PK":"COMPANY#8fd4728b-89b6-40aa-a57a-85a4672ec9a0", "SK":"#METADATA#8fd4728b-89b6-40aa-a57a-85a4672ec9a0"}, ReturnConsumedCapacity='TOTAL')

    except ClientError as e:
        print(e.response["Error"]["Message"])
        return _response(500, {"status": "DynamoDB Client Error"})
    except KeyError as e:
        print(e)
        return _response(404, {"status": "ITEM NOT FOUND"})
    else:
        record = DataStore.clean_item(data["Item"])
        print("GetItem succeeded:")
        print(json.dumps(data, indent=4, cls=DecimalEncoder))

    return _response(200, {"data": record})


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, cls=DecimalEncoder),
    }
