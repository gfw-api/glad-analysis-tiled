from functools import wraps

from flask import request

from utils import util
from gladAnalysis.errors import Error


def get_geojson(func):
    """Grab geojson any way it comes - with geostore ID,
       with wdpa ID or use ID, or just POSTed geojson.
       Convert this into a dictionary object and return
       it as the variable `geojson`
    """
    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.method == 'GET':
            geostore_id = request.args.get('geostore')
            use_type = request.view_args.get('use_type')
            wdpa_id = request.view_args.get('wdpa_id')

            # if it's a GET request, we know it has to have
            # either geostore ID, use ID, or wdpa ID
            # we'll use the geostore to look up each of these geometries
            # so build the geostore URI accordingly
            if geostore_id:
               geostore_uri = '/geostore/{}'.format(geostore_id)

            # convert use_type & use_id into a geostore ID
            # important for serialization - that's how we'll build a download url
            elif use_type:
                use_id = request.view_args.get('use_id')
                geostore_uri = '/geostore/use/{}/{}'.format(use_type, use_id)

                # no longer need use_id or use_type - have already converted
                # these to a geostore_uri, which will then give us geojson
                # and geostore_id
                del kwargs['use_id'], kwargs['use_type']

            elif wdpa_id:
                geostore_uri = '/geostore/wdpa/{}'.format(wdpa_id)
                del kwargs['wdpa_id']

            else:
                raise Error('Geostore or geojson must be set')

            # grab the geojson from the geostore
            geostore_query = util.query_microservice(geostore_uri)
            kwargs["geostore_id"] = geostore_query['data']['id']
            geojson = geostore_query['data']['attributes']['geojson']

        # if it's a POST, we should find the geojson in the `geojson` property of the body
        elif request.method == 'POST':
            geojson = request.get_json().get('geojson', None) if request.get_json() else None

        if not geojson:
            raise Error('Geostore or geojson must be set')

        # add geojson variable to kwargs so it's accessible in our routes
        kwargs["geojson"] = geojson

        return func(*args, **kwargs)
    return wrapper

