"""API ROUTER"""

import sys
from flask import jsonify, Blueprint, request, Response

from CTRegisterMicroserviceFlask import request_to_microservice
import json

from gladAnalysis.services import custom_geom_queries
from gladAnalysis.utils import util
from gladAnalysis.serializers import serialize_response


custom_geom_endpoints = Blueprint('custom_geom_endpoints', __name__)

@custom_geom_endpoints.route('/', methods=['POST'])
def glad_custom_geom():

    query_params = util.get_query_params(request)

    geojson = request.get_json().get('geojson', None) if request.get_json() else None

    resp = custom_geom_queries.calc_stats(geojson)

    # format glad alerts to be "count": 4, "week": 5, "year": 2017, etc
    # response = serialize_response(request, formatted_glad, glad_area)
    return jsonify(resp)
