import json
import datetime
from collections import defaultdict
from functools import partial
from shapely.ops import transform

from shapely.geometry import shape

from CTRegisterMicroserviceFlask import request_to_microservice


def get_shapely_geom(geojson):
    # geojson = geom['geojson']

    if not isinstance(geojson, dict):
        raise ValueError('Unable to decode input geojson')

    if not geojson.get('features'):
        raise ValueError('No features in geojson')

    if len(geojson['features']) > 1:
        raise ValueError('Currently accepting only 1 feature at a time')

    # grab the actual geometry-- that's the level on which shapely operates
    try:
        aoi_geom = shape(geojson['features'][0]['geometry'])
    except:
        raise ValueError('Unable to decode input geojson')

    if 'Polygon' not in aoi_geom.type:
        raise ValueError('Geometry type must be polygon or multipolygon')

    return aoi_geom


def create_resp_dict(date_dict):
    k = date_dict.keys() # alert date = datetime.datetime(2015, 6, 4, 0, 0)
    v = date_dict.values() # count

    resp_dict = {
                 'year': grouped_and_to_rows([x.year for x in k], v, 'year'),
                 # month --> quarter calc: https://stackoverflow.com/questions/1406131
                 'quarter': grouped_and_to_rows([(x.year, (x.month-1)//3 + 1) for x in k], v, 'quarter'),
                 'month':  grouped_and_to_rows([(x.year, x.month) for x in k], v, 'month'),
                 'week': grouped_and_to_rows([(x.year, x.isocalendar()[1]) for x in k], v, 'week'),
                 'day': grouped_and_to_rows([(x.year, x.strftime('%Y-%m-%d')) for x in k], v, 'day'),
                 'total': sum(v)
                }

    return resp_dict


def grouped_and_to_rows(keys, vals, agg_type):

    # source: https://jakevdp.github.io/blog/2017/03/22/group-by-from-scratch/
    count = defaultdict(int)
    for key, val in zip(keys, vals):
        count[key] += val
    grouped = dict(count)

    final_list = []

    for key, val in grouped.iteritems():

        if agg_type == 'year':
            row = {agg_type: key}
        else:
            row = {'year': key[0], agg_type: key[1]}

        row['count'] = val
        final_list.append(row)

    return final_list


def date_to_julian(in_date):
    fmt = '%Y-%m-%d'
    in_date_format = datetime.datetime.strptime(in_date, fmt)
    tt = in_date_format.timetuple()
    j_day = tt.tm_yday

    year = in_date.split('-')[0]

    return int(year), int(j_day)


def get_query_params(request):
    # possible params: gladConfirmOnly, aggregate_values, aggregate_by
    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', None)
    confidence = request.args.get('gladConfirmOnly', False)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2001-01-01,{}'.format(today))
    query_params = 'gladConfirmOnly={}&period={}'.format(confidence, period)
    if agg_values:
        query_params += '&aggregate_values={}&aggregate_by={}'.format(agg_values, agg_by)

    return query_params


def route_constructor(iso_code, adm1_code=None, adm2_code=None):
    route = iso_code
    if adm1_code:
        route += '/{}'.format(adm1_code)
        if adm2_code:
            route += '/{}'.format(adm2_code)

    return route


def query_microservice(uri):

    config_alerts = {
        'uri': uri,
        'method': 'GET',
        'ignore_version': True
    }

    return request_to_microservice(config_alerts)


def format_alerts(request, glad_alerts):
    # take the glad alerts format and strip out some attributes
    agg_by = request.args.get('aggregate_by', None)
    print glad_alerts

    if len(glad_alerts['data']['attributes']['value']) == 1:
        return glad_alerts['data']['attributes']['value'][0]['alerts']
    else:
        formatted_alerts = []
        for d in glad_alerts['data']['attributes']['value']:

            alerts_dict = {}
            alerts_dict['count'] = d['alerts']

            if agg_by:
                alerts_dict[agg_by] = d[agg_by]

            formatted_alerts.append(alerts_dict)

        return formatted_alerts

