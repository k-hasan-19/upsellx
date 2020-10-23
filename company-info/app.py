import os
import re
import json
import boto3
from botocore.exceptions import ClientError
from encoder_class import DecimalEncoder
from datastore import DataStore


def lambda_handler(event, context):
    company_domain = event["queryStringParameters"]["domain"].strip()
    if not valid_domain(company_domain):
        return _response(400, {"message": "Invalid request body"})
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
        _start_state_machine(company_domain)
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


def _start_state_machine(domain):
    state_machine_arn = os.getenv("STATE_MACHINE_ARN")
    if os.getenv("AWS_SAM_LOCAL") == "true":
        state_machine_arn = "arn:aws:states:us-west-2:660076225786:stateMachine:ParallelStateMachine-JHpcmWykb5w7"
    client = boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn=state_machine_arn, input=json.dumps({"domain": domain})
    )
    # print(json.dumps(response))


def valid_domain(domain):
    domain_regex = r"(([\da-zA-Z])([_\w-]{,62})\.){,127}(([\da-zA-Z])[_\w-]{,61})?([\da-zA-Z]\.((xn\-\-[a-zA-Z\d]+)|([a-zA-Z\d]{2,})))"

    domain_regex = "{0}$".format(domain_regex)
    valid_domain_name_regex = re.compile(domain_regex, re.IGNORECASE)
    domain = domain.lower().strip()
    if re.match(valid_domain_name_regex, domain):
        return True
    else:
        return False
