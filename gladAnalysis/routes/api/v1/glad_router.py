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
    print "HERE I AM "
    # Query glad-alerts/summary-stats
    query_params = util.get_query_params(request)
    route = util.route_constructor(iso_code, adm1_code, adm2_code)

    alerts_uri = '/glad-alerts/summary-stats/admin/{}?{}'.format(route, query_params)
    area_uri = '/geostore/admin/{}'.format(route)

    glad_alerts = util.query_microservice(alerts_uri)

    glad_area = util.query_microservice(area_uri)['data']['attributes']['areaHa']

    formatted_glad = util.format_alerts(request, glad_alerts)
    # format glad alerts to be "count": 4, "week": 5, "year": 2017, etc
    response = serialize_response(request, formatted_glad, glad_area)
    return jsonify(response)


# test iso download - need to flesh this out further
@glad_analysis_endpoints.route('/test.csv', methods=['GET'])
def test_bra1():

    # https://stackoverflow.com/a/16890018
    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket('gfw2-data')

    def generate():
        for f in bucket_obj.list(prefix='alerts-tsv/temp/glad-by-state/BRA/BRA_1.csv'):
            unfinished_line = ''
            for byte in f:
                byte = unfinished_line + byte
                lines = byte.split('\n')
                unfinished_line = lines.pop()
                for line in lines:
                    yield line + '\n'

            yield unfinished_line

    return Response(generate(), mimetype='text/csv')
