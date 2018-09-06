"""API ROUTER"""
from flask import jsonify, Blueprint, request, Response
from boto.s3.connection import S3Connection

from gladAnalysis.utils import util
from gladAnalysis.serializers import serialize_response

glad_analysis_endpoints = Blueprint('glad_analysis_endpoints', __name__)


@glad_analysis_endpoints.route('/admin/<iso_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
def glad_stats_iso(iso_code, adm1_code=None, adm2_code=None):

    # Query glad-alerts/summary-stats
    query_params = util.get_query_params(request)
    route = util.route_constructor(iso_code, adm1_code, adm2_code)

    alerts_uri = '/glad-alerts/summary-stats/admin/{}?{}'.format(route, query_params)
    area_uri = '/v2/geostore/admin/{}'.format(route)

    # if it's just an iso, simplify the geostore because we only really want the area_ha
    if not adm1_code:
        area_uri += '?simplify=0.05'

    glad_alerts = util.query_microservice(alerts_uri)
    glad_area = util.query_microservice(area_uri)['data']['attributes']['areaHa']

    formatted_glad = util.format_alerts(request, glad_alerts)
    # format glad alerts to be "count": 4, "week": 5, "year": 2017, etc

    # package up iso/adm1/adm2 to limit # of params passed to function
    id_tuple = (iso_code, adm1_code, adm2_code)

    response = serialize_response(request, formatted_glad, glad_area, None, id_tuple)

    return jsonify(response)

