import json
import unittest

import mercantile
from shapely.geometry import shape

from gladAnalysis.utils.tile_geometry import build_tile_dict


class TilingTest(unittest.TestCase):
    def test_tile_geom(self):
        # load src geojson
        with open('tests/fixtures/BRA_src.geojson') as src:
            geojson = json.load(src)

        # load tiled output
        with open('tests/fixtures/BRA_tiled.geojson') as src:
            tiled_geojson = json.load(src)

        # grab actual geom
        geom = shape(geojson['features'][0]['geometry'])

        # start empty feature collection
        tiled_features = {'type': 'FeatureCollection', 'features': []}

        # cut our geom into tiles
        tile_dict = build_tile_dict(geom)

        # grab the shape of these tiles so we can visualize it
        for t, pct_intersect in tile_dict.items():
            tile_geom = mercantile.feature(t)
            tile_geom['properties']['tile_coverage_fraction'] = pct_intersect

            tiled_features['features'].append(tile_geom)

        # compare to our saved version of the tiled geometry
        # this includes tile_fraction calcs as well
        self.assertEqual(json.dumps(sorted(tiled_geojson)), json.dumps(sorted(tiled_features)))
