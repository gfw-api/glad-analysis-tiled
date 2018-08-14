"""API ROUTER"""
from flask import jsonify, Blueprint, request, Response
from boto.s3.connection import S3Connection

from gladAnalysis.utils import util
from gladAnalysis.serializers import serialize_response
from gladAnalysis.services import download_service

glad_analysis_endpoints = Blueprint('glad_analysis_endpoints', __name__)


@glad_analysis_endpoints.route('/admin/<iso_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>', methods=['GET'])
@glad_analysis_endpoints.route('/admin/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
def glad_stats_iso(iso_code, adm1_code=None, adm2_code=None):

    # Query glad-alerts/summary-stats
    query_params = util.get_query_params(request)
    route = util.route_constructor(iso_code, adm1_code, adm2_code)

    alerts_uri = '/glad-alerts/summary-stats/admin/{}?{}'.format(route, query_params)
    area_uri = '/geostore/admin/{}'.format(route)
    glad_alerts = util.query_microservice(alerts_uri)

    glad_area = util.query_microservice(area_uri)['data']['attributes']['areaHa']

    formatted_glad = util.format_alerts(request, glad_alerts)
    # format glad alerts to be "count": 4, "week": 5, "year": 2017, etc
    response = serialize_response(request, formatted_glad, glad_area, None, route)

    return jsonify(response)


# send ISO, download from s3
@glad_analysis_endpoints.route('/download/<iso_code>/', methods=['GET'])
@glad_analysis_endpoints.route('/download/<iso_code>/<adm1_code>/', methods=['GET'])
@glad_analysis_endpoints.route('/download/<iso_code>/<adm1_code>/<adm2_code>/', methods=['GET'])
def glad_download_iso_input(iso_code, adm1_code=None, adm2_code=None):

    streaming = download_service.iso_download(request, iso_code, adm1_code, adm2_code)

    def generate():
        for row in streaming:
            if row:
                yield row + '\n'

    return Response(generate(), mimetype='text/csv')

