from CTRegisterMicroserviceFlask import request_to_microservice

from gladAnalysis.errors import Error


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


def format_alerts_admin(request, glad_alerts):
    # take the glad alerts format and strip out some attributes
    agg_by = request.args.get('aggregate_by', None)

    for elem in glad_alerts['data']['attributes']['value']:
        if 'alerts' not in elem:
            raise Error('Inner API call returned no alerts.', 500)

    if len(glad_alerts['data']['attributes']['value']) == 1:
        return glad_alerts['data']['attributes']['value'][0]['alerts']
    else:
        formatted_alerts = []
        for d in glad_alerts['data']['attributes']['value']:

            alerts_dict = {}
            alerts_dict['count'] = d['alerts']

            if agg_by:
                alerts_dict[agg_by] = d[agg_by]
                if agg_by != 'year' and agg_by in ['day', 'week', 'quarter', 'month']:
                    alerts_dict['year'] = d['year']

            formatted_alerts.append(alerts_dict)

        return formatted_alerts
