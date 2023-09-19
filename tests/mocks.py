import re


def mock_geostore(mocker):
    matcher = re.compile(".*/geostore.*")
    return mocker.get(
        matcher,
        request_headers={
            "content-type": "application/json",
            "x-api-key": "api-key-test",
        },
        status_code=200,
        json={
            "data": {
                "type": "geoStore",
                "id": "8a3864a0eb61aa4830d99a3c416d9deb",
                "attributes": {
                    "geojson": {
                        "features": [
                            {
                                "properties": {},
                                "type": "Feature",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-71.71875, -26.4312280645064],
                                            [-36.2109375, -26.4312280645064],
                                            [-36.2109375, 2.81137119333114],
                                            [-71.71875, 2.81137119333114],
                                            [-71.71875, -26.4312280645064],
                                        ]
                                    ],
                                },
                            }
                        ],
                        "crs": {},
                        "type": "FeatureCollection",
                    },
                    "hash": "8a3864a0eb61aa4830d99a3c416d9deb",
                    "provider": {},
                    "areaHa": 1245852113.7189505,
                    "bbox": [
                        -71.71875,
                        -26.4312280645064,
                        -36.2109375,
                        2.81137119333114,
                    ],
                    "lock": False,
                    "info": {"use": {}},
                },
            }
        },
    )
