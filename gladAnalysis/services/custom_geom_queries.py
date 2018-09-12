import argparse
import json
import sys
import logging
import sqlite3

import requests
from flask import request
from shapely.geometry import shape

from gladAnalysis.utils import tile_geometry, sqlite_util, util, geom_to_db
from gladAnalysis import middleware
from gladAnalysis.serializers import serialize_response


def calc_stats(geojson, request, geostore_id=None):
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
            geom = geom.simplify(0.05).buffer(0)
        
        # find all tiles that intersect the aoi, calculating a proportion of overlap for each
        tile_dict = tile_geometry.build_tile_dict(geom)

        # connect to vector tiles / sqlite3 database
        dbname = geom_to_db.get_db_name(geom)
        conn, cursor = sqlite_util.connect(dbname)

        # insert intersect list into mbtiles database as tiles_aoi
        sqlite_util.insert_intersect_table(cursor, tile_dict, False)

        # query the database for summarized results
        rows = sqlite_util.select_within_tiles(cursor)

        # combine rows into one dictionary
        alert_date_dict = util.row_list_to_json(rows)

        if alert_date_dict:
            return middleware.format_alerts_custom_geom(alert_date_dict, request, geostore_id, geom_area_ha)
        else:
            return serialize_response(request, 0, geom_area_ha, geostore_id)

    else:
        logging.info('geometry is < 10 million ha. Passing to raster lambda function ')
        url = 'https://0kepi1kf41.execute-api.us-east-1.amazonaws.com/dev/glad-alerts'
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({'geojson': {'type': 'FeatureCollection', 'features': [geojson['features'][0]]}})

        r = requests.post(url, data=payload, headers=headers, params=request.args.to_dict())

        response_dict = r.json()

        alerts_dict = response_dict['data']['attributes']['value']
        geom_area = response_dict['data']['attributes']['area_ha']

        # #serialize response
        serialized = serialize_response(request, alerts_dict, geom_area, geostore_id)

        return serialized

