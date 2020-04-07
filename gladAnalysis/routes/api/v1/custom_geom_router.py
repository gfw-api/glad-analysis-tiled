"""API ROUTER"""
import requests
from flask import Blueprint, request, Response, stream_with_context

from gladAnalysis.errors import Error
from gladAnalysis.middleware import get_geojson
from gladAnalysis.services import custom_geom_queries
from gladAnalysis.validators import validate_geojson, validate_args_custom_glad, validate_period_arg

custom_geom_endpoints = Blueprint('custom_geom_endpoints', __name__)


@custom_geom_endpoints.route('/', methods=['GET', 'POST'])
@custom_geom_endpoints.route('/use/<use_type>/<use_id>', methods=['GET'])
@custom_geom_endpoints.route('/wdpa/<wdpa_id>', methods=['GET'])
@get_geojson
@validate_geojson
@validate_args_custom_glad
def custom_stats(geojson, geostore_id=None):
    # what is this middlware magic? how do we get rid of WDPA + Use params?
    # Use @get_geojson to get geojson + geostore ID
    # the geostore ID is what we'll use in the download URLs response

    return custom_geom_queries.calc_stats(geojson, request, geostore_id)


@custom_geom_endpoints.route('/download', methods=['GET', 'POST'])
@get_geojson
@validate_geojson
@validate_period_arg
def custom_download(geojson, geostore_id=None):
    # http://flask.pocoo.org/snippets/118/
    url = 'https://0kepi1kf41.execute-api.us-east-1.amazonaws.com/dev/glad-alerts/download'
    req = requests.post(url, json={"geojson": geojson}, stream=True, params=request.args.to_dict())

    content_type = "text/csv" if request.args.get('format', 'json') == "csv" else "application/json"

    return Response(stream_with_context(req.iter_content(chunk_size=1024)),
                    content_type=content_type)


@custom_geom_endpoints.errorhandler(Error)
def handle_error(error):
    return error.serialize
