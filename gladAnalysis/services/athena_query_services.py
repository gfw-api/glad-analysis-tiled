import datetime
from io import StringIO
from dateutil.relativedelta import relativedelta

import boto3
from shapely.geometry import Polygon
# from gladAnalysis import middleware
from gladAnalysis.middleware import AthenaWaiter, get_s3_results_in_dict

# import AthenaWaiter, get_s3_results_in_dict


class GladPointsGenerator(object):

    def __init__(self, geom_wkt, agg_by, period):
        self.geom_wkt = geom_wkt
        self.period = period
        self.agg_by = agg_by
        self.bucket = 'gfw2-data'
        self.folder = 'alerts-tsv/glad_download/'

    # return sql of Select either a count of alerts, or a count grouped by year and day
    def get_query_string(self):

        if self.period:
            min_date = self.period.split(',')[0]
            max_date = self.period.split(',')[-1]
        else:
            today = datetime.datetime.now()
            min_date = (today - relativedelta(years=2)).strftime('%Y-%m-%d')
            max_date = today.strftime('%Y-%m-%d')


        if self.agg_by:

            sql = '''SELECT year, julian_day, COUNT(*) AS alert_count '''
            '''FROM glad_admin '''
            '''WHERE ST_Intersects(ST_Polygon('{}'), ST_Point(lon, lat)) '''
            '''GROUP BY year, julian_day'''.format(self.geom_wkt)

        else:
            sql = '''SELECT '0' as year, '0' as julian_day, COUNT(*) AS alert_count '''
            '''FROM glad_admin '''
            '''WHERE ST_Intersects(ST_Polygon('{}'), ST_Point(lon, lat)) '''.format(self.geom_wkt)

        return sql

    # execute the query in athena. saves it to gfw2-data/alerts-tsv/glad_download/
    # returns the name of the csv (query id). output has 3 columns
    def get_query_id(self):
        client = boto3.client(
            'athena',
            region_name='us-east-1'
        )
        response = client.start_query_execution(
            QueryString=self.get_query_string(),
            QueryExecutionContext={
                'Database': 'default'
            },
            ResultConfiguration={
                'OutputLocation': 's3://{0}/{1}'.format(
                    self.bucket,
                    self.folder

                )
            }
        )

        return response['QueryExecutionId']

    # gets the name of the csv file saved on s3
    def get_results_key(self, query_id):
        return '{0}/{1}.csv'.format(self.folder, query_id)

    # waits for query to execute, then returns dictionary
    def get_results_df(self, query_id):
        waiter = middleware.AthenaWaiter(max_tries=100)
        waiter.wait(
            bucket=self.bucket,
            key=self.get_results_key(query_id),
            query_id=query_id
        )

        date_count_dict = middleware.get_s3_results_in_dict(
                self.get_results_key(query_id),
                self.bucket
        )

        return date_count_dict  # should look like [{'year': '0', 'julian_day': '0', 'alert_count': '508'},{},{}]

    def generate(self):
        query_id = self.get_query_id()

        return self.get_results_df(query_id)

