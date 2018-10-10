import argparse
import json
import sys
import logging
import sqlite3

import requests
from flask import request
from shapely.geometry import shape, Polygon

from gladAnalysis.utils import tile_geometry, sqlite_util, aggregate_response
from gladAnalysis.serializers import serialize_response


def calc_stats(geojson, request, geostore_id):
    """Given an input geojson and (optionally) some params
       (period, agg_by, etc), calculate the # of alerts in an AOI"""

    geom = shape(geojson['features'][0]['geometry'])
    geom_area_ha = tile_geometry.calc_area(geom, proj='aea')

    # check if it's too big to send to raster analysis
    # current cutoff is 10,000,000 ha, or about the size of Kentucky
    if geom_area_ha > 10000000:
        logging.info("Geometry is larger than 10 million ha. Tiling request")

        # simplify geometry if it's large
        if sys.getsizeof(json.dumps(geojson)) > 100000:
            if geom.geom_type == 'Polygon':
                geom = Polygon(geom.simplify(0.05).buffer(0).exterior)
            else:
                geom = MultiPolygon(geom.simplify(0.05).buffer(0))

        # find all tiles that intersect the aoi, calculating a proportion of overlap for each
        tile_dict = tile_geometry.build_tile_dict(geom)

        # insert intersect list into mbtiles database as tiles_aoi
        conn, cursor = sqlite_util.connect()
        sqlite_util.insert_intersect_table(cursor, tile_dict)

        # query the database for summarized results for our AOI
        rows = sqlite_util.select_within_tiles(cursor, request)

        # aggregate as necessary into week/month/year
        alerts_dict = aggregate_response.format_alerts_geom(rows, request)

    else:
        logging.info('geometry is < 10 million ha. Passing to raster lambda function ')
        url = 'https://0kepi1kf41.execute-api.us-east-1.amazonaws.com/dev/glad-alerts'

        kwargs = {'json': {'geojson': geojson},
                  'headers': {'Content-Type': 'application/json'},
                  'params': request.args.to_dict()}

        r = requests.post(url, **kwargs)
        alerts_dict = r.json()['data']['attributes']['value']

    return serialize_response(request, alerts_dict, geom_area_ha, geostore_id)
