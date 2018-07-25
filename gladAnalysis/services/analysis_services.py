import athena_query_services
from gladAnalysis import middleware


def point_in_poly_download(geom, agg_by, period):

    generator = athena_query_services.GladPointsGenerator(geom, agg_by, period)

    # list of alerts
    alerts_list = generator.generate() # ex:[{'year': '2016', 'julian_day': '217', 'alert_count': '508'},{},{}]

    # filter by period and aggregate response if necessary
    cleaned_response = middleware.create_resp_dict(alerts_list, period, agg_by)
    # then serialize
    return alerts_list

print 'done!'
