import os
import time
import boto3


class DataStore:
    @staticmethod
    def clean_item(item):
        item.pop("PK", None)
        item.pop("SK", None)
        return item

    @staticmethod
    def profile_keys(domain):
        PK = "Company" + "#" + domain
        SK = "profile"
        return (
            PK,
            SK,
        )

    @staticmethod
    def get_table_client():
        table_name = os.getenv("TABLE_NAME")
        if os.getenv("AWS_SAM_LOCAL") == "true":
            table_name = "upsellx-stack-table"
        # AWS_REGION_DYNAMODB = os.getenv("AWS_REGION_DYNAMODB")
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        return table
