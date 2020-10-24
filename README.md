### upsellx

#### TODO

- [x] REST API
- [x] Web Crawlers(2)
- [x] Parallelization
- [x] NoSQL Database
- [x] ETL
- [ ] Pipeline Scheduler

### Deployment
```bash
cd layers/dependencies/nodejs/ && npm install && cd -
pip install -r layers/dependencies/python/requirements.txt --target layers/dependencies/python/ --no-cache-dir
sam deploy --guided
```
## Architecture

![App Architecture](https://raw.githubusercontent.com/k-hasan-19/upsellx/master/images/UpSellx.png)
