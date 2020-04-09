# v1.0.0

## 09/04/2020

- Update k8s configuration with node affinity.

## 16/02/2020

- Set correct `content-type` response header on `/download` endpoint, depending on requested format:
  - `application/json` for `format=json` (default format)
  - `text/csv` for `format=csv`
