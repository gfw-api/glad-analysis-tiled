"""API ROUTER"""

import sys
from flask import jsonify, Blueprint, request, Response


from gladAnalysis.services import analysis_services, download_service, athena_query_services
glad_analysis_endpoints = Blueprint('glad_analysis_endpoints', __name__)


@glad_analysis_endpoints.route('/', methods=['POST'])
def glad_stats():
    geojson = request.get_json().get('geojson', None) if request.get_json() else None

    summary_stats = analysis_services.point_in_poly_stats(geojson, 'week', '2017-01-01,2017-06-01')
    return jsonify(summary_stats)


# send geom, get download
@glad_analysis_endpoints.route('/from_geom.csv', methods=['POST'])
def glad_download_geom_input():
    geojson = request.get_json().get('geojson', None) if request.get_json() else None
    streaming = analysis_services.point_in_poly_download(geojson)

    def generate():
        for row in streaming:
            yield row + '\n'

    return Response(generate(), mimetype='text/csv')


# send ISO, download from s3
@glad_analysis_endpoints.route('/download/<iso_code>', methods=['GET'])
@glad_analysis_endpoints.route('/download/<iso_code>/<adm1_code>', methods=['GET'])
@glad_analysis_endpoints.route('/download/<iso_code>/<adm1_code>/<adm2_code>', methods=['GET'])
def glad_download_iso_input(iso_code, adm1_code=None, adm2_code=None):

    streaming = analysis_services.iso_download(request, iso_code, adm1_code, adm2_code)

    def generate():
        for row in streaming:
            if row:
	        yield row + '\n'

    return Response(generate(), mimetype='text/csv')

