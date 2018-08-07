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


def serialize_response(request, glad_alerts, glad_area):
    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', None)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2015-01-01,{}'.format(today))

    serialized_resopnse = {
        "data": {
        "attributes": {
                        "areaHa": glad_area,
                        "downloadUrls": {"csv": "/download/db3", "json": "/download/db34c2"},
                        "value": glad_alerts
                        },
        "id": '20892bc2-5601-424d-8a4a-605c319418a2',
        "period": period,
        "type": 'glad-alerts'
        }
        }

    if agg_values:
        serialized_resopnse['data']['aggregate_by'] = agg_by
        serialized_resopnse['data']['aggregate_values'] = True


    return serialized_resopnse

