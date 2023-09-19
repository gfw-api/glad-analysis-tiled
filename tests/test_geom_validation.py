import os

import requests_mock
from RWAPIMicroservicePython.test_utils import mock_request_validation


root_path = "/api/v1/glad-alerts-athena"


@requests_mock.Mocker(kw="mocker")
def test_no_geojson(client, mocker):
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))
    response = client.post(
        root_path,
        json={"geojson": {}},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert response.json["errors"][0]["detail"] == "Geostore or geojson must be set"


@requests_mock.Mocker(kw="mocker")
def test_no_type(client, mocker):
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))
    response = client.post(
        root_path,
        json={"geojson": {"this": "ok"}},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "Invalid geojson- must have type property"
    )


@requests_mock.Mocker(kw="mocker")
def test_no_features(client, mocker):
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))

    response = client.post(
        root_path,
        json={"geojson": {"type": "FeatureCollection"}},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "feature collection must have features object"
    )


@requests_mock.Mocker(kw="mocker")
def test_too_many_features(client, mocker):
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))

    response = client.post(
        root_path,
        json={"geojson": {"type": "FeatureCollection", "features": [1, 2]}},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "input geojson must have only one feature"
    )


@requests_mock.Mocker(kw="mocker")
def test_no_coordinates(client, mocker):
    aoi = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "geometry": {"type": "polygon"}}],
    }
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))

    response = client.post(
        root_path,
        json={"geojson": aoi},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "Invalid geojson - geometry does not have proper type or coordinates objects"
    )


@requests_mock.Mocker(kw="mocker")
def test_line_geom(client, mocker):
    aoi = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-57, -15], [-56, -18], [-57, -19], [-58, -19]],
                },
            }
        ],
    }
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))

    response = client.post(
        root_path,
        json={"geojson": aoi},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "input geojson must be of geometry type polygon or multipolygon"
    )


@requests_mock.Mocker(kw="mocker")
def test_invalid_polygon(client, mocker):
    # last coordinate has only one value
    aoi = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-57, -17], [-57, -15], [-60, -15], [-60]]],
        },
    }
    mock_request_validation(mocker, microservice_token=os.getenv("MICROSERVICE_TOKEN"))

    response = client.post(
        root_path,
        json={"geojson": aoi},
        follow_redirects=True,
        headers={"x-api-key": "api-key-test"},
    )
    assert (
        response.json["errors"][0]["detail"]
        == "Error converting input geometry into shapely object; check input geojson"
    )
