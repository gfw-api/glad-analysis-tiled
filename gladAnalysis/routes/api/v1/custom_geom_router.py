"""API ROUTER"""
from flask import jsonify, Blueprint, request, Response, stream_with_context
import requests
from CTRegisterMicroserviceFlask import request_to_microservice

from gladAnalysis.services import custom_geom_queries
from gladAnalysis.utils import util


custom_geom_endpoints = Blueprint('custom_geom_endpoints', __name__)


@custom_geom_endpoints.route('/', methods=['GET', 'POST'])
def custom_stats():
    print 'in custom stats'

    if request.method == 'GET':
        geostore_id = request.args.get('geostore', None)

        geostore_uri = '/geostore/{}'.format(geostore_id)

        geojson = util.query_microservice(geostore_uri)
        
        resp = geojson

    else:

        geojson = request.get_json().get('geojson', None) if request.get_json() else None

        resp = custom_geom_queries.calc_stats(geojson, request)

    return jsonify(resp)


@custom_geom_endpoints.route('/download', methods=['POST'])
def custom_download():

    query_params = util.get_query_params(request)

    geojson = request.get_json().get('geojson', None) if request.get_json() else None

    # http://flask.pocoo.org/snippets/118/
    url = 'https://3bkj4476d9.execute-api.us-east-1.amazonaws.com/dev/glad-alerts/download'
    req = requests.post(url, json={"geojson": geojson}, stream=True, params=request.args.to_dict())

    return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type = req.headers['content-type'])
