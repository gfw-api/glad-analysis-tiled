import unittest
import json

import requests

from gladAnalysis import app


class GeomValidationTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def deserialize_error(self, response):
        return json.loads(response.data)['errors'][0]['detail']

    def post_geom(self, geom):

        url = '/api/v1/glad-alerts-athena'
        data = {'geojson': geom}
        response = self.app.post(url, json=data, follow_redirects=True)
        error = self.deserialize_error(response)
        status_code = response.status_code

        # and do our check to make sure the error code is correct here
        # that way we don't have to do it every time below
        self.assertEqual(status_code, 400)

        return error

    def test_no_geojson(self):

        error_text = self.post_geom({})
        self.assertEqual(error_text, 'Geostore or geojson must be set')

    def test_no_type(self):

        error_text = self.post_geom({'this': 'ok'})
        self.assertEqual(error_text, 'Invalid geojson- must have type property')

    def test_no_features(self):

        error_text = self.post_geom({'type': 'FeatureCollection'})
        self.assertEqual(error_text, 'feature collection must have features object')

    def test_too_many_features(self):

        error_text = self.post_geom({'type': 'FeatureCollection', 'features': [1, 2]})
        self.assertEqual(error_text, 'input geojson must have only one feature')

    def test_no_coordinates(self):
        aoi = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'polygon'}}]}
        error_text = self.post_geom(aoi)
        self.assertEqual(error_text, 'Invalid geojson - geometry does not have proper type or coordinates objects')

    def test_line_geom(self):
        aoi = {"type":"FeatureCollection","features":[
                  {"type":"Feature","properties":{},"geometry":
                      {"type":"LineString","coordinates":[[-57,-15],[-56,-18],[-57,-19],[-58,-19]]}
               }]}
        error_text = self.post_geom(aoi)
        self.assertEqual(error_text, 'input geojson must be of geometry type polygon or multipolygon')

    def test_invalid_polygon(self):

        # last coordinate has only one value
        aoi = {'type': 'Feature', 'geometry': {'type': 'Polygon', 'coordinates': [[[-57,-17],[-57,-15],[-60,-15],[-60]]]}}
        error_text = self.post_geom(aoi)
        self.assertEqual(error_text, 'Error converting input geometry into shapely object; check input geojson')

