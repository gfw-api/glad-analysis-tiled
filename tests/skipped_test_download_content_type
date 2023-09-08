import datetime
import json
import unittest

from httmock import all_requests, HTTMock, response

from gladAnalysis import app


class ParamsTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def deserialize_error(self, response):
        return json.loads(response.data)['errors'][0]['detail']

    def deserialize_body(self, response):
        return json.loads(response.data)

    def make_request(self, request):
        with HTTMock(geostore_mock):
            response = self.app.get(request, follow_redirects=True)

        return response

    def test_quotes_in_period(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download?geostore=xxx&period="2013-01-01,2014-01-01"')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response),
                         "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

    def test_bogus_period(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=2016-01-01,2013-01-01')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response), 'Start date must be less than end date')

    def test_one_period(self):
        response = self.make_request('/api/v1/glad-alerts-athena/download?geostore=xxxx&period=2016-01-01')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response), 'Period needs 2 arguments')

    def test_wrong_period(self):
        response = self.make_request('/api/v1/glad-alerts-athena/download?geostore=xxxx&period=2016-30-01,2016-01-01')

        self.assertEqual(response.status_code, 400)

        self.assertEqual(self.deserialize_error(response), "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

    def test_early_period(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=1999-01-01,2016-01-01')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response), "Start date can't be earlier than 2015-01-01")

    def test_late_period(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=2015-01-01,2025-01-01')

        today = datetime.datetime.now()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response), "End year can't be later than {}".format(today.year))

    def test_no_geostore(self):
        response = self.make_request('/api/v1/glad-alerts-athena/download')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.deserialize_error(response), 'Geostore or geojson must be set')

    def test_default_format_content_type(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=2019-01-01,2020-01-01')

        body = self.deserialize_body(response)
        self.assertEqual('application/json', response.content_type)
        self.assertIn('data', body)
        self.assertIn('attributes', body['data'])
        self.assertIn('type', body['data'])
        self.assertIn('id', body['data'])

    def test_json_format_content_type(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=2019-01-01,2020-01-01&format=json')

        body = self.deserialize_body(response)
        self.assertEqual('application/json', response.content_type)
        self.assertIn('data', body)
        self.assertIn('attributes', body['data'])
        self.assertIn('type', body['data'])
        self.assertIn('id', body['data'])

    def test_csv_format_content_type(self):
        response = self.make_request(
            '/api/v1/glad-alerts-athena/download/?geostore=xxxx&period=2019-01-01,2020-01-01&format=csv')

        body = self.deserialize_body(response)
        self.assertEqual('text/csv', response.content_type)
        self.assertIn('data', body)
        self.assertIn('attributes', body['data'])
        self.assertIn('type', body['data'])
        self.assertIn('id', body['data'])


@all_requests
def geostore_mock(url, request):
    # necessary because geostore validation happens before param validation

    headers = {'content-type': 'application/json'}
    content = {"data": {"type": "geoStore", "id": "8a3864a0eb61aa4830d99a3c416d9deb", "attributes": {"geojson": {
        "features": [{"properties": {}, "type": "Feature", "geometry": {"type": "Polygon", "coordinates": [
            [[-71.71875, -26.4312280645064], [-36.2109375, -26.4312280645064], [-36.2109375, 2.81137119333114],
             [-71.71875, 2.81137119333114], [-71.71875, -26.4312280645064]]]}}], "crs": {},
        "type": "FeatureCollection"}, "hash": "8a3864a0eb61aa4830d99a3c416d9deb", "provider": {},
        "areaHa": 1245852113.7189505,
        "bbox": [-71.71875,
                 -26.4312280645064,
                 -36.2109375,
                 2.81137119333114],
        "lock": False,
        "info": {
            "use": {}}}}}

    return response(200, content, headers, None, 5, request)
