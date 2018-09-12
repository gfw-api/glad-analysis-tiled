"""VALIDATORS"""
from functools import wraps

from shapely.geometry import shape

from gladAnalysis.errors import Error


def validate_geojson(func):
    """validate input geojson"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        # grab geojson from our function parameters
        geojson = kwargs['geojson']

        # check if it's a featurecollection or a feature
        gj_type = geojson.get('type')

        if not gj_type:
            raise Error('Invalid geojson- must have type property')

        # convert to a featurecollection - that's our preferred format
        if gj_type.lower() == 'feature':
            geojson = {"type": "FeatureCollection", "features": [ geojson ]}
        
        # if it's a featurecollection, just make sure that it has features
        elif gj_type.lower() == 'featurecollection':
             if not geojson.get('features'):
                 raise Error('feature collection must have features object')
        else:
            raise Error('input geojson must be of type feature collection or feature')

        if len(geojson['features']) > 1:
            raise Error('input geojson must have only one feature')

        try:
            geom = geojson['features'][0]['geometry']
            geom_type = geom['type']
            geom_type = geom['coordinates']
        except:
            raise Error('Invalid geojson - geometry does not have proper type or coordinates objects')

        if geojson['features'][0]['geometry']['type'].lower() not in ['polygon', 'multipolygon']:
            raise Error('input geojson must be of geometry type polygon or multipolygon')

        # if all else passes, try converting it to a shapely shape
        try:
            shape(geom)
        except:
            raise Error('Error converting input geometry into shapely object; check input geojson')

        # return updated geojson to our function
        kwargs['geojson'] = geojson 

        return func(*args, **kwargs)
    return wrapper

