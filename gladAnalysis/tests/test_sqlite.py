import json
import unittest

import mercantile

from gladAnalysis import app
from gladAnalysis.utils import sqlite_util


class SqliteTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False

        test_db = 'gladAnalysis/tests/fixtures/stats.db'
        conn, self.cursor = sqlite_util.connect(test_db)

        # create temp table of tiles from our test AOI
        self.create_temp_table()

    def create_temp_table(self):
        # load tiled output - in this case to just grab tile IDs for our AOI
        with open('gladAnalysis/tests/fixtures/BRA_tiled.geojson') as src:
            tiled_geojson = json.load(src)

        # create empty tile_dict - the input for our join table
        tile_dict = {}

        for feat in tiled_geojson['features']:
            title = feat['properties']['title']

            # separate x/y/z coords from serialized tile format (XYZ tile Tile(x=1403, y=2255, z=12))
            title = title.replace('=', ' ').replace(',', ' ').strip(')').split()
            x, y, z = [int(x) for x in title if x.isdigit()]
            t = mercantile.Tile(x, y, z)

            # then add this with tile_coverage_fraction to tile_dict
            tile_coverage_fraction = feat['properties']['tile_coverage_fraction']
            tile_dict[t] = tile_coverage_fraction

        # insert into our test db
        sqlite_util.insert_intersect_table(self.cursor, tile_dict)

    def test_all_alerts(self):
        req = MockRequest()
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0][1], 87293)
        self.assertEqual(len(data), 1)

    def test_agg_by(self):
        # Don't actually specify what to agg_by here, given sqlite's poor
        # date parsing capabilities. Will just GROUP BY date
        req = MockRequest(agg_by=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0], ('2015-01-03', 146))
        self.assertEqual(data[-1], ('2018-09-09', 0))
        self.assertEqual(len(data), 240)

    def test_date_filter(self):
        req = MockRequest(period='2015-10-04,2017-01-01')
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0][1], 16930)
        self.assertEqual(len(data), 1)

    def test_conf_filter(self):
        req = MockRequest(gladConfirmOnly=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0][1], 78290)
        self.assertEqual(len(data), 1)

    def test_date_and_conf_filter(self):
        req = MockRequest(period='2018-01-01,2018-10-04', gladConfirmOnly=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0][1], 18307)
        self.assertEqual(len(data), 1)

    def test_agg_and_conf_filter(self):
        req = MockRequest(agg_by=True, gladConfirmOnly=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0], ('2015-01-03', 146))
        self.assertEqual(data[-1], ('2018-09-07', 43))
        self.assertEqual(len(data), 235)

    def test_date_and_agg_filter(self):
        req = MockRequest(period='2018-01-01,2018-10-04', agg_by=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0], ('2018-01-18', 155))
        self.assertEqual(data[-1], ('2018-09-09', 0))
        self.assertEqual(len(data), 47)

    def test_filter_all(self):
        req = MockRequest(period='2015-02-07,2018-09-13', agg_by=True, gladConfirmOnly=True)
        data = sqlite_util.select_within_tiles(self.cursor, req)

        self.assertEqual(data[0], ('2015-02-12', 1))
        self.assertEqual(data[-1], ('2018-09-07', 43))
        self.assertEqual(len(data), 231)


class MockRequest(object):

    def __init__(self, agg_by=None, period=None, gladConfirmOnly=None):
        self.args = {}
        self.args['aggregate_by'] = agg_by
        self.args['period'] = period
        self.args['gladConfirmOnly'] = gladConfirmOnly
