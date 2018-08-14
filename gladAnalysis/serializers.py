"""Serializers"""
import datetime

from gladAnalysis.utils import util


def build_download_urls(geostore_uri, agg_values, agg_by, period, conf, format):

     if geostore_uri:
         print geostore_uri
         print 'OK THIS IS GEOSTORE ABOVE '
         geostore_id = util.query_microservice(geostore_uri)['data']['id']

         url = 'glad-alerts-athena/download/?period={}&gladConfirmOnly={}&aggregate_values={}&' \
               'aggregate_by={}&geostore={}'.format(period, conf, agg_values, agg_by, geostore_id)

         url += '&format={}'

         return url.format('csv'), url.format('json')

     else:
         return None, None



def serialize_response(request, glad_alerts, glad_area, geostore_uri=None):

    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', False)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2015-01-01,{}'.format(today))
    conf = request.args.get('gladConfirmOnly', False)

    if agg_by:
        glad_alerts = sorted(glad_alerts, key=lambda k: k[agg_by])

    csv_url, json_url = build_download_urls(geostore_uri, agg_values, agg_by, period, conf, 'csv')

    serialized_response = {
        "data": {
        "attributes": {
                        "downloadUrls": {"csv": csv_url, "json": json_url},
                        "value": glad_alerts
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

