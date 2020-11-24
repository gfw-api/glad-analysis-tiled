# GLAD Analysis API Microservice Overview

[![Build Status](https://travis-ci.com/gfw-api/glad-analysis-tiled.svg?branch=dev)](https://travis-ci.com/gfw-api/glad-analysis-tiled)
[![Test Coverage](https://api.codeclimate.com/v1/badges/55617d7d21d384ce68e6/test_coverage)](https://codeclimate.com/github/gfw-api/glad-analysis-tiled/test_coverage)

Query the GLAD and forest loss datasets with the [Global Forest Watch (GFW)](http://globalforestwatch.org) API

- Analyze datasets by a custom area of interest using the [GFW Geostore API](https://github.com/gfw-api/gfw-geostore-api) or by sending GeoJson in Post
- Analyze datasets by Country, State and Districts (defined by the [GADM Database](http://www.gadm.org/))
- Analyze datasets by GFW Land Use features (Managed Forest Concessions, Oil Palm Concessions, Mining Concessions and Wood Fiber Concessions- available in select countries)
- Analyze datasets by Protected Areas (defined by the [WDPA database](http://www.wdpa.org/))
- Get dataset download urls (csv and json) for areas of interest
- Summarize analysis results by day, week, month, quarter or year
- Get the date of the most recent alert

## API Endpoints
For endpoint documentation, please visit our [API documentation page for GLAD](https://production-api.globalforestwatch.org/documentation/#/?tags=GLAD)

## Dependencies

You will need [Control Tower](https://github.com/control-tower/control-tower) up and running - either natively or with Docker. Refer to the project's README for information on how to set it up.

The Dataset microservice is built using [Node.js](https://nodejs.org/en/), and can be executed either natively or using Docker, each of which has its own set of requirements.

Native execution requires:
- [Python 2.7](https://www.python.org/)

Execution using Docker requires:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

Dependencies on other Microservices:
- [Geostore](https://github.com/gfw-api/gfw-geostore-api/)
- [Fires Summary Stats](https://github.com/gfw-api/fires-summary-stats/)

## Getting Started
Perform the following steps:
* [Install docker](https://docs.docker.com/engine/installation/)
* [Install control tower](https://github.com/control-tower/control-tower)
* clone Repo `git clone https://github.com/gfw-api/glad-analysis-tiled`
* CD into diretory `cd glad-analysis-tiled`
* Copy env file `cp dev.env.sample dev.env`
* Change content accordingly 
* Run in develop mode
```ssh
./gladAnalysis.sh develop
```

If this is the first time you run it, it may take a few minutes.

## Testing
Testing API endpoints

```ssh
./gladAnalysis.sh test
```

## Config

## register.json
This is the configuration file for the rest endpoints in the microservice. This json connects to the API Gateway. It contains variables such as:
* #(service.id) => Id of the service set in the config file by environment
* #(service.name) => Name of the service set in the config file by environment
* #(service.uri) => Base uri of the service set in the config file by environment

Example:
````
{
    "id": "#(service.id)",
    "name": "#(service.name)",
    "tags": ["gfw"],
    "urls": [{
        "url": "/v1/glad-alerts/admin/:iso_code",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v1/glad-alerts-athena/admin/:iso_code"
        }]
    }, {
        "url": "/v1/glad-alerts/admin/:iso_code/:admin_id",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v1/glad-alerts-athena/admin/:iso_code/:admin_id"
        }]
    }, {
        "url": "/v1/glad-alerts/admin/:iso_code/:admin_id/:dist_id",
        "method": "GET",
        "endpoints": [{
            "method": "GET",
            "path": "/api/v1/glad-alerts-athena/admin/:iso_code/:admin_id/:dist_id"
        }]
    }]
}

'''
