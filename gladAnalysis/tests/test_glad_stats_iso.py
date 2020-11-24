import json
import unittest
from httmock import HTTMock, response, urlmatch
from gladAnalysis import app


class ParamsTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    @staticmethod
    def deserialize_error(res):
        return json.loads(res.data)['errors'][0]['detail']

    @staticmethod
    def deserialize_body(res):
        return json.loads(res.data)

    def test_glad_stats_with_no_alerts(self):
        with HTTMock(glad_summary_stats_no_alerts_mock), HTTMock(geostore_mock):
            res = self.app.get('/api/v1/glad-alerts-athena/admin/BRA', follow_redirects=True)
            self.assertEqual(res.status_code, 500)
            self.assertEqual(self.deserialize_error(res), "Inner API call returned no alerts.")

    def test_glad_stats_only_one_with_alerts(self):
        with HTTMock(glad_summary_stats_only_one_with_many_alerts_mock), HTTMock(geostore_mock):
            res = self.app.get('/api/v1/glad-alerts-athena/admin/BRA', follow_redirects=True)
            self.assertEqual(res.status_code, 500)
            self.assertEqual(self.deserialize_error(res), "Inner API call returned no alerts.")

    def test_glad_stats_with_one_alert(self):
        with HTTMock(glad_summary_stats_with_one_alert_mock), HTTMock(geostore_mock):
            res = self.app.get('/api/v1/glad-alerts-athena/admin/BRA', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

    def test_glad_stats_with_more_than_one_alert(self):
        with HTTMock(glad_summary_stats_with_many_alerts_mock), HTTMock(geostore_mock):
            res = self.app.get('/api/v1/glad-alerts-athena/admin/BRA', follow_redirects=True)
            self.assertEqual(res.status_code, 200)


@urlmatch(path='/v2/geostore/admin/BRA')
def geostore_mock(url, request):
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


@urlmatch(path='/glad-alerts/summary-stats/admin/BRA')
def glad_summary_stats_no_alerts_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": {"aggregate_admin": None, "aggregate_by": None, "aggregate_time": None, "aggregate_values": None,
                        "attributes": {
                            "value": [{
                                "gladConfirmOnly": False,
                                "iso": "BRA",
                                "polyname": "admin",
                                "sum": 173023338
                            }]},
                        "gladConfirmOnly": False, "period": "2015-01-01,2020-11-23", "polyname": "admin"}}

    return response(200, content, headers, None, 5, request)


@urlmatch(path='/glad-alerts/summary-stats/admin/BRA')
def glad_summary_stats_with_one_alert_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": {"aggregate_admin": None, "aggregate_by": None, "aggregate_time": None, "aggregate_values": None,
                        "attributes": {
                            "value": [{
                                "gladConfirmOnly": False,
                                "iso": "BRA",
                                "polyname": "admin",
                                "sum": 173023338,
                                "alerts": []
                            }]},
                        "gladConfirmOnly": False, "period": "2015-01-01,2020-11-23", "polyname": "admin"}}

    return response(200, content, headers, None, 5, request)


@urlmatch(path='/glad-alerts/summary-stats/admin/BRA')
def glad_summary_stats_with_many_alerts_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": {"aggregate_admin": None, "aggregate_by": None, "aggregate_time": None, "aggregate_values": None,
                        "attributes": {
                            "value": [
                                {
                                    "gladConfirmOnly": False,
                                    "iso": "BRA",
                                    "polyname": "admin",
                                    "sum": 173023338,
                                    "alerts": []
                                },
                                {
                                    "gladConfirmOnly": False,
                                    "iso": "BRA",
                                    "polyname": "admin",
                                    "sum": 173023338,
                                    "alerts": []
                                },
                            ]},
                        "gladConfirmOnly": False, "period": "2015-01-01,2020-11-23", "polyname": "admin"}}

    return response(200, content, headers, None, 5, request)


@urlmatch(path='/glad-alerts/summary-stats/admin/BRA')
def glad_summary_stats_only_one_with_many_alerts_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": {"aggregate_admin": None, "aggregate_by": None, "aggregate_time": None, "aggregate_values": None,
                        "attributes": {
                            "value": [
                                {
                                    "gladConfirmOnly": False,
                                    "iso": "BRA",
                                    "polyname": "admin",
                                    "sum": 173023338
                                },
                                {
                                    "gladConfirmOnly": False,
                                    "iso": "BRA",
                                    "polyname": "admin",
                                    "sum": 173023338,
                                    "alerts": []
                                },
                            ]},
                        "gladConfirmOnly": False, "period": "2015-01-01,2020-11-23", "polyname": "admin"}}

    return response(200, content, headers, None, 5, request)
