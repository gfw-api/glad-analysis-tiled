import athena_query_services
from gladAnalysis import middleware
from gladAnalysis.utils import util, flask_stream_files
import download_service
import datetime


def point_in_poly_stats(geom, agg_by, period):

    geom_wkt = util.get_shapely_geom(geom)
    generator = athena_query_services.GladPointsGenerator(geom_wkt, agg_by, period)

    # list of alerts
    alerts_list = generator.generate() # ex:[{'year': '2016', 'julian_day': '217', 'alert_count': '508'},{},{}]

    # filter by period and aggregate response if necessary
    cleaned_response = middleware.create_resp_dict(alerts_list, period, agg_by)
    # then serialize
    return cleaned_response


def point_in_poly_download(geom):
    geom_wkt = util.get_shapely_geom(geom)

    generator = athena_query_services.GladPointsGenerator(geom_wkt, download=True)

    query_id = generator.get_query_id()

    bucket, folder = generator.bucket_folder()

    user_period = '2016-01-01,2016-06-01'
    user_start = user_period.split(',')[0]
    user_end = user_period.split(',')[1]

    start_year, start_day = util.date_to_julian(user_start)
    end_year, end_day = util.date_to_julian(user_end)

    # return query_id
    return download_service.download_csv(bucket, folder, query_id, start_year, end_year, start_day, end_day)





