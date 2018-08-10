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







