"""VALIDATORS"""
import datetime

from functools import wraps

from shapely.geometry import shape
from flask import jsonify, Blueprint, request

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


def validate_args_custom_glad(func):
    """Validate user arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        validate_aggregate()

        validate_period()

        return func(*args, **kwargs)

    return wrapper


def validate_period_arg(func):
    """Validate period arg"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_period()
        return func(*args, **kwargs)
    return wrapper


def validate_period():

    # validate period
    today = datetime.datetime.now()
    period = request.args.get('period', None)
    minYear = 2015
    if period:

        if len(period.split(',')) < 2:
            raise Error("Period needs 2 arguments")

        else:
            if '"' in period or "'" in period:
                raise Error("Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD (no quotes)")

            period_from = period.split(',')[0]
            period_to = period.split(',')[1]

            try:
                period_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
                period_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')
            except ValueError:
                raise Error("Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

            if period_from.year < minYear:
                raise Error("Start date can't be earlier than {}-01-01".format(minYear))

            if period_to.year > today.year:
                raise Error("End year can't be later than {}".format(today.year))

            if period_from > period_to:
                raise Error('Start date must be less than end date')


def validate_aggregate():

    # validate aggregate
    agg_by = request.args.get('aggregate_by')
    agg_values = request.args.get('aggregate_values')
    iso = request.view_args.get('iso_code', None)

    agg_list = ['day', 'week', 'quarter', 'month', 'year', 'adm1', 'adm2']

    if iso == 'global':
        agg_list = [x for x in agg_list if x not in ['adm2']]
        agg_list.append('iso')

    if agg_values:
        if agg_values.lower() not in ['true', 'false']:
            raise Error("aggregate_values parameter must be either true or false")

        agg_values = eval(agg_values.title())

    # validate aggregating with global summary
    if agg_values and agg_by:

        if agg_by.lower() not in agg_list:
            raise Error("aggregate_by must be specified as one of: {} ".format(", ".join(agg_list)))

        if agg_by and not agg_values:
            raise Error("aggregate_values parameter must be true in order to aggregate data")

        if agg_values and not agg_by:
            raise Error("if aggregate_values is TRUE, aggregate_by parameter must be specified " \
                   "as one of: {}".format(", ".join(agg_list)))
