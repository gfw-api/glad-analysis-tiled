import datetime

from utils import util

from gladAnalysis.serializers import serialize_response


def format_alerts_custom_geom(alert_date_dict, request, geostore_id, geom_area_ha=None):
    agg_by = request.args.get('aggregate_by', None)
    # filter alerts
    alerts_filtered = util.filter_alerts(alert_date_dict, request)

    # create dictionary of agg by day, week, month, etc
    grouped = util.create_resp_dict(alerts_filtered)

    # get the agg by value
    if agg_by:
        final_vals = grouped[agg_by]

    else:
        final_vals = grouped['total']

    return serialize_response(request, final_vals, geom_area_ha, geostore_id)


def create_resp_dict(alerts_list, period=None, agg_by=None):

    start = period.split(',')[0]
    end = period.split(',')[1]

    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')

    # add a real date column and filter for period
    date_formatted_dict = {}
    date_unformatted_dict = {}

    for date_count_dict in alerts_list:

        # get day and year, count
        j_day = date_count_dict['julian_day']
        alert_year = date_count_dict['year']

        # create date by combining julian day and year
        date_obj = datetime.datetime(alert_year, 1, 1) + datetime.timedelta(j_day)

        # create new key of alert_date
        date_count_dict['alert_date'] = date_obj

        # filter for period
        if start_date <= date_count_dict['alert_date'] <= end_date:
            date_unformatted_dict[date_obj] = date_count_dict['alert_count']
            # get the string format of the date
            date_str = date_obj.strftime('%Y-%m-%d')
            date_formatted_dict[date_str] = date_count_dict['alert_count']

    if agg_by:
        date_formatted_dict = util.create_resp_dict(date_unformatted_dict)
        # get just the requested agg by
        date_formatted_dict = date_formatted_dict[agg_by]

    return date_formatted_dict

