### upsellx

#### TODO

- [x] REST API
- [x] Web Crawlers(2)
- [x] Parallelization
- [x] NoSQL Database
- [x] ETL
- [x] Pipeline Scheduler

### Deployment
```bash
cd layers/node/nodejs/ && npm install && cd -

pip install -r layers/py/python/requirements.txt --target layers/py/python/ --no-cache-dir
sam deploy --guided
```
## Architecture

![App Architecture](https://raw.githubusercontent.com/k-hasan-19/upsellx/master/images/UpSellx.png)
