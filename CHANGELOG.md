## 16/02/2020

- Set correct `content-type` response header on `/download` endpoint, depending on requested format:
  - `application/json` for `format=json` (default format)
  - `text/csv` for `format=csv`
