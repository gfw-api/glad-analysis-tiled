"""Serializers"""
import datetime

from gladAnalysis.utils import util


def build_download_urls(id_tuple, geostore_id, agg_values, agg_by, period, conf):

    # id_tuple is the combination of iso, adm1, adm2
    if id_tuple:

        iso_code, adm1_code, adm2_code = id_tuple
        download_path = 'http://gfw2-data.s3.amazonaws.com/alerts-tsv/glad-download/'

        if adm2_code:
           download_path += 'adm2/{iso}/{adm1}/{iso}_{adm1}_{adm2}.csv'
        elif adm1_code:
            download_path += 'adm1/{iso}/{iso}_{adm1}.csv'
        else:
            download_path += 'iso/{iso}.csv'

        return download_path.format(iso=iso_code, adm1=adm1_code, adm2=adm2_code), None
      
    else:

        download_path = '/glad-alerts-athena/download/'
        url = '{}?period={}&gladConfirmOnly={}&aggregate_values={}&' \
           'aggregate_by={}'.format(download_path, period, conf, agg_values, agg_by)
    
        if geostore_id:
            url += '&geostore={}'.format(geostore_id)
    
        url += '&format={}'
    
        return url.format('csv'), url.format('json')


def serialize_response(request, glad_alerts, glad_area, geostore_id=None, id_tuple=None):

    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', False)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    period = request.args.get('period', '2015-01-01,{}'.format(today))
    conf = request.args.get('gladConfirmOnly', False)

    if agg_by:
        glad_alerts = sorted(glad_alerts, key=lambda k: k[agg_by])

    csv_url, json_url = build_download_urls(id_tuple, geostore_id, agg_values, agg_by, period, conf)

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

