import os
from datetime import datetime
import awswrangler as wr


def lambda_handler(event, context):
    domains = os.getenv("DOMAINS").split(",")
    temp_bucket = os.getenv("TEMP_BUCKET")
    source_db = os.getenv("SOURCE_DATABASE")
    silo_bucket = os.getenv("SILO_BUCKET")
    dest_db = os.getenv("DEST_DATABASE")

    date_now = _date_now()
    # print(domains.split(","))
    path = "s3://{bucket}/{domain}"
    path_with_date = "s3://{bucket}/{domain}/" + date_now + "/"
    for domain in domains:
        df = wr.s3.read_json(
            path=path_with_date.format(bucket=temp_bucket, domain=domain), dataset=True
        )
        wr.s3.to_parquet(
            df=df,
            path=path.format(bucket=silo_bucket, domain=domain),
            use_threads=True,
            compression="snappy",
            schema_evolution=True,
            dataset=True,
            database=dest_db,  # Athena/Glue database
            table=domain.strip(),  # Athena/Glue table
        )


def _date_now():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")
