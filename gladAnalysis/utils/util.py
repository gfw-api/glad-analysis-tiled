import json
import datetime
from collections import Counter, defaultdict

from shapely.geometry import shape
from CTRegisterMicroserviceFlask import request_to_microservice

from gladAnalysis.errors import Error


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
        'method': 'GET'
    }

    if 'geostore' in uri:
        config_alerts['uri'] = '/v2' + uri
        config_alerts['ignore_version'] = True

    response = request_to_microservice(config_alerts)

    if response.get('errors'):
        raise Error(**response['errors'][0])

    else:
        return response


def format_alerts(request, glad_alerts):
    # take the glad alerts format and strip out some attributes
    agg_by = request.args.get('aggregate_by', None)

    if len(glad_alerts['data']['attributes']['value']) == 1:
        return glad_alerts['data']['attributes']['value'][0]['alerts']
    else:
        formatted_alerts = []
        for d in glad_alerts['data']['attributes']['value']:

            alerts_dict = {}
            alerts_dict['count'] = d['alerts']

            if agg_by:
                alerts_dict[agg_by] = d[agg_by]
                if not agg_by == 'year':
                    alerts_dict['year'] = d['year']

            formatted_alerts.append(alerts_dict)

        return formatted_alerts


def row_list_to_json(row_list, period=None, confirm_only=False):

    # NB: include period and confidence filter at some point

    # https://stackoverflow.com/a/11011846/
    final_date_dict = Counter()

    for row in row_list:

        date_conf_dict = json.loads(row[0])
        proportion_covered = row[1]

        # update each value by the proportion covered of each tile
        # not spatially accurate, obviously, but better than binary 1|0
        # https://stackoverflow.com/a/16993582/
        date_conf_dict.update((x, y*proportion_covered) for x, y in date_conf_dict.items())

        # adding Counters will add dicts, summing values where we have
        # overlapping keys
        final_date_dict += Counter(date_conf_dict)

    # convert all to int
    return dict((x, int(y)) for x, y in final_date_dict.items())


def filter_alerts(alert_date_dict, request):

    confidence_param = request.args.get('gladConfirmOnly', False)

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2001-01-01,{}'.format(today))

    start_date = period.split(',')[0]
    end_date = period.split(',')[1]

    start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    filtered_dict = {}
    for key, val in alert_date_dict.iteritems():

        alert_date = key.split("::")[0]
        alert_date_obj = datetime.datetime.strptime(alert_date, '%Y-%m-%d')
        confidence = str(key.split("::")[1])
        if confidence_param: ## filter to just get conf=3

            if (start_date_obj <= alert_date_obj <= end_date_obj) and confidence == '3':

                filtered_dict[alert_date_obj] = val

        else:
            if start_date_obj <= alert_date_obj <= end_date_obj:

                try:
                    filtered_dict[alert_date_obj] += val
                except KeyError:
                    filtered_dict[alert_date_obj] = val

    return filtered_dict

