### upsellx

#### TODO

- [x] REST API
- [x] Web Crawlers(2)
- [x] Parallelization
- [x] NoSQL Database
- [x] ETL
- [x] Pipeline Scheduler

### Deployment(sam-cli)
```bash
cd layers/node/nodejs/ && npm install && cd -
pip install -r layers/py/python/requirements.txt --target layers/py/python/ --no-cache-dir
sam deploy --guided
```

### Usage
* Api doc [here](https://app.swaggerhub.com/apis/k-hasan-19/upsellx/0.2.0)
* Api summary: After submiting the crawling job using `POST` you query company data using the `GET` API. Endpoint accepts *FQDN*/`hostname`  
* To query data at temporary bucket goto Athena console and select `upsellxtemp` database
* Scheduler will compress data everyday in parquet && will append to `upsellxsilo` database. To access it early run `aws-data-wrangler` lambda function from aws console.
## Architecture

![App Architecture](https://raw.githubusercontent.com/k-hasan-19/upsellx/master/images/UpSellx.png)
