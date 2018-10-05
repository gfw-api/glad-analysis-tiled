import unittest
import json
import datetime

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

    def make_request(self, request):

        with HTTMock(geostore_mock):
            response = self.app.get(request, follow_redirects=True)
        error = self.deserialize_error(response)
        status_code = response.status_code

        # and do our check to make sure the error code is correct here
        # that way we don't have to do it every time below
        self.assertEqual(status_code, 400)

        return error

    def test_quotes_in_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxx&period="2013-01-01,2014-01-01"')

        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

    def test_bogus_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena/?geostore=xxxx&period=2016-01-01,2013-01-01')

        self.assertEqual(error_text, 'Start date must be less than end date')

    def test_one_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxxx&period=2016-01-01')

        self.assertEqual(error_text, 'Period needs 2 arguments')

    def test_wrong_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxxx&period=2016-30-01,2016-01-01')

        self.assertEqual(error_text, "Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

    def test_early_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena/?geostore=xxxx&period=1999-01-01,2016-01-01')

        self.assertEqual(error_text, "Start date can't be earlier than 2015-01-01")

    def test_late_period(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena/?geostore=xxxx&period=2015-01-01,2025-01-01')

        today = datetime.datetime.now()
        self.assertEqual(error_text, "End year can't be later than {}".format(today.year))

    def test_agg_values_not_boolean(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxx&aggregate_values=maybe&aggregate_by=adm1')
        self.assertEqual(error_text, 'aggregate_values parameter must be either true or false')

    def test_bad_agg_by(self):
        agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'adm2']
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxx&aggregate_values=True&aggregate_by=iso')
        self.assertEqual(error_text, "aggregate_by must be specified as one of: {} ".format(", ".join(agg_list)))

    def test_no_agg_values(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxx&aggregate_by=week')
        self.assertEqual(error_text, "aggregate_values parameter must be true in order to aggregate data")

    def test_no_agg_by(self):
        agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'adm2']
        error_text = self.make_request('/api/v1/glad-alerts-athena?geostore=xxx&aggregate_values=True')
        self.assertEqual(error_text, "if aggregate_values is TRUE, aggregate_by parameter must be " \
                                     "specified as one of: {}".format(", ".join(agg_list)))

    def test_no_geostore(self):
        error_text = self.make_request('/api/v1/glad-alerts-athena')
        self.assertEqual(error_text, 'Geostore or geojson must be set')


@all_requests
def geostore_mock(url, request):
    # necessary because geostore validation happens before param validation

    headers = {'content-type': 'application/json'}
    content = {"data":{"type":"geoStore","id":"8a3864a0eb61aa4830d99a3c416d9deb","attributes":{"geojson":{"features":[{"properties":{},"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-71.71875,-26.4312280645064],[-36.2109375,-26.4312280645064],[-36.2109375,2.81137119333114],[-71.71875,2.81137119333114],[-71.71875,-26.4312280645064]]]}}],"crs":{},"type":"FeatureCollection"},"hash":"8a3864a0eb61aa4830d99a3c416d9deb","provider":{},"areaHa":1245852113.7189505,"bbox":[-71.71875,-26.4312280645064,-36.2109375,2.81137119333114],"lock":False,"info":{"use":{}}}}}

    return response(200, content, headers, None, 5, request)

