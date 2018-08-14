"""API ROUTER"""
from flask import jsonify, Blueprint, request, Response, stream_with_context
import requests
from CTRegisterMicroserviceFlask import request_to_microservice

from gladAnalysis.services import custom_geom_queries
from gladAnalysis.utils import util


custom_geom_endpoints = Blueprint('custom_geom_endpoints', __name__)


@custom_geom_endpoints.route('/', methods=['GET', 'POST'])
@custom_geom_endpoints.route('/use/<use_type>/<use_id>', methods=['GET'])
@custom_geom_endpoints.route('/wdpa/<wdpa_id>', methods=['GET'])
def custom_stats(wdpa_id=None, use_type=None, use_id=None):

    if request.method == 'GET':
        geostore_id = request.args.get('geostore', None)
        geostore_uri = '/geostore/{}'.format(geostore_id)

        if wdpa_id:
            geostore_uri = '/geostore/wdpa/{}'.format(wdpa_id)

        if use_type:
            geostore_uri = '/geostore/use/{}/{}'.format(use_type, use_id) #

        geojson = util.query_microservice(geostore_uri)['data']['attributes']['geojson']

        resp = custom_geom_queries.calc_stats(geojson, request, geostore_uri)

        return jsonify(resp)

    else:

        geojson = request.get_json().get('geojson', None) if request.get_json() else None

        resp = custom_geom_queries.calc_stats(geojson, request)

    return jsonify(resp)


@custom_geom_endpoints.route('/download', methods=['GET', 'POST'])
def custom_download():

    if request.method == 'POST':
        geojson = request.get_json().get('geojson', None) if request.get_json() else None

    if request.method == 'GET':
        geostore_id = request.args.get('geostore')
        geostore_uri = '/geostore/{}'.format(geostore_id)

        geojson = util.query_microservice(geostore_uri)['data']['attributes']['geojson']

    # http://flask.pocoo.org/snippets/118/
    url = 'https://3bkj4476d9.execute-api.us-east-1.amazonaws.com/dev/glad-alerts/download'
    req = requests.post(url, json={"geojson": geojson}, stream=True, params=request.args.to_dict())

    return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type = req.headers['content-type'])

