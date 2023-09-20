"""API ROUTER"""
import urllib

from flask import Blueprint, request

from gladAnalysis.errors import Error
from gladAnalysis.serializers import serialize_response, serialize_latest
from gladAnalysis.utils import util, sqlite_util

glad_analysis_endpoints = Blueprint('glad_analysis_endpoints', __name__)


@glad_analysis_endpoints.route('/admin/<iso_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
def glad_stats_iso(iso_code, adm1_code=None, adm2_code=None):
    # Query glad-alerts/summary-stats
    query_params = params = request.args.to_dict()
    route = util.route_constructor(iso_code, adm1_code, adm2_code)

    alerts_uri = '/v1/glad-alerts/summary-stats/admin/{}?{}'.format(route, urllib.parse.urlencode(query_params))
    area_uri = '/v2/geostore/admin/{}'.format(route)

    # if it's just an iso, simplify the geostore because we only really want the area_ha
    if not adm1_code:
        area_uri += '?simplify=0.05'

    glad_alerts = util.query_microservice(alerts_uri, request.headers.get('x-api-key'))
    aoi_area_ha = util.query_microservice(
        area_uri, request.headers.get('x-api-key'))['data']['attributes']['areaHa']

    # format glad alerts to be "count": 4, "week": 5, "year": 2017, etc
    formatted_glad = util.format_alerts_admin(request, glad_alerts)

    # package up iso/adm1/adm2 to limit # of params passed to function
    id_tuple = (iso_code, adm1_code, adm2_code)

    return serialize_response(request, formatted_glad, aoi_area_ha, None, id_tuple)


@glad_analysis_endpoints.route('/latest', methods=['GET'])
def latest():
    latest_data = sqlite_util.get_latest()

    return serialize_latest(latest_data)


@glad_analysis_endpoints.errorhandler(Error)
def handle_error(error):
    return error.serialize
