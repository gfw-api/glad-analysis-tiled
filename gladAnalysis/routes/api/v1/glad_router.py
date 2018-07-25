"""API ROUTER"""

import logging

from flask import jsonify, Blueprint, request
from gladAnalysis.routes.api import error
from gladAnalysis.validators import validate_greeting

from gladAnalysis.serializers import serialize_greeting
import json
import CTRegisterMicroserviceFlask

from gladAnalysis.services import analysis_services, download_service
glad_analysis_endpoints = Blueprint('glad_analysis_endpoints', __name__)

# accept geometry/geostore or iso. needs a period, needs agg by


def summarize_data(geostore_id=None, download=None, iso_code=None, adm1_code=None, adm2_code=None, period=None):

    if geostore_id:
        print "construct a query, send to athena. "

        if download:
            alert_list = analysis_services.point_in_poly_download(geostore_id, period)

    else:
        print "construct a query, send to athena. "
        if download:
            print "streaming csv to download"


@glad_analysis_endpoints.route('/glad-alerts', methods=['POST'])
def glad_geom():
    geojson = request.get_json().get('geojson', None) if request.get_json() else None
    print geojson
    return None
    # return jsonify(summarize_data(aoi))
