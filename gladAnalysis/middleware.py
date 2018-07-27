
import time
import datetime
import sys

import boto3
import botocore
from botocore.client import Config
from io import StringIO
import csv
from utils import util


def get_s3_client():
    return boto3.client(
        's3', 'us-east-1', config=Config(
            s3={'addressing_style': 'path'}
        )
    )


# put the csv into a dictionary
def get_s3_results_in_dict(key, bucket):

    s3_client = get_s3_client()
    data = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )

    s3_result_uni = data['Body'].read().decode("utf-8")
    stringio_s3 = StringIO(s3_result_uni)

    # reader is returned as line seperated lists: ['2016-05-07', '208']
    reader = csv.reader(stringio_s3, skipinitialspace=True)

    # skip header row
    next(reader, None)
    alerts_list = []
    for row in reader:

        alerts_dict = {}
        alerts_dict['year'] = int(row[0])
        alerts_dict['julian_day'] = int(row[1])
        alerts_dict['alert_count'] = int(row[2])
        alerts_list.append(alerts_dict)

    return alerts_list


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


class AthenaWaiterException(Exception):
    pass


class AthenaWaiter(object):
    """Not only can wait more than the AWS S3 waiter,
    but it also checks if the query has failed
    or was canceled and stops instead of waiting
    until it times out.
    """

    def __init__(self, max_tries=30, interval=1):
        self.s3_client = get_s3_client()
        self.athena_client = boto3.client(
            'athena',
            region_name='us-east-1'
        )
        self.max_tries = max_tries
        self.interval = interval

    def object_exists(self, bucket='', key=''):
        # print "\n\nChecking if {0} and {1} exist\n\n".format(bucket, key)
        exists = True
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as exc:
            if exc.response['Error']['Code'] == '404':
                exists = False
            else:
                raise
        return exists

    def check_status(self, query_id):
        status = self.athena_client.get_query_execution(
            QueryExecutionId=query_id
        )['QueryExecution']['Status']
        if status['State'] in ['FAILED', 'CANCELLED']:
            raise AthenaWaiterException(
                'Query Error: {0}'
                .format(status['StateChangeReason'])
            )

    def wait(self, bucket='', key='', query_id=''):

        success = False
        for _ in range(self.max_tries):

            if self.object_exists(bucket=bucket, key=key):

                success = True
                break
            self.check_status(query_id)
            time.sleep(self.interval)
        if not success:
            raise AthenaWaiterException(
                'Exceeded the maximum number of tries ({0})'
                .format(self.max_tries)
            )
