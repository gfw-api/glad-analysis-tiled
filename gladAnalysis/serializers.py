"""Serializers"""
import datetime


def serialize_greeting(greeting):
    """."""
    return {
        'id': None,
        'type': 'greeting',
        'attributes': {
            'word': greeting.get('word', None),
            'propertyTwo': greeting.get('propertyTwo', None),
            'propertyThree': greeting.get('propertyThree', None),
            'something': greeting.get('something', None),
        }
    }


def serialize_response(request, glad_alerts, glad_area=None):

    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', False)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2015-01-01,{}'.format(today))
    conf = request.args.get('gladConfirmOnly', False)

    # sort alerts
    glad_alerts_sorted = sorted(glad_alerts, key=lambda k: k[agg_by])
    serialized_response = {
        "data": {
        "attributes": {
                        "downloadUrls": {"csv": None, "json": None},
                        "value": glad_alerts_sorted
                        },
        "id": '20892bc2-5601-424d-8a4a-605c319418a2',
        "period": period,
        "type": 'glad-alerts'
        }
        }

    if agg_values:
        serialized_response['data']['aggregate_by'] = agg_by
        serialized_response['data']['aggregate_values'] = True

    if glad_area:
        serialized_response['data']['attributes']['areaHa'] = glad_area

    if conf == 'True':
        conf = True
    serialized_response['data']['gladConfirmOnly'] = conf
    return serialized_response
