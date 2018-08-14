from flask import Flask
from flask import Response
from flask import jsonify
app = Flask(__name__)
from shapely.geometry import shape

import boto3

from boto.s3.connection import S3Connection
import datetime
from gladAnalysis.utils import util


def parse_period(period):
    print 'PERIOD: {}'.format(period)
    user_start = period.split(',')[0]
    user_end = period.split(',')[1]

    start_year, start_day = util.date_to_julian(user_start)
    end_year, end_day = util.date_to_julian(user_end)

    return start_year, end_year, start_day, end_day


def download_csv(bucket, path, query_id, conf, user_period, adm1_code=None, adm2_code=None):
    # read and filter a single csv
    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket(bucket)

    result_key = '{0}/{1}.csv'.format(path, query_id)
    key_obj = bucket_obj.lookup(result_key)

    headers = ['longitude', 'latitude', 'confidence', 'year', 'julian_day', 'iso', 'adm1', 'adm2', 'confidence_text']
    yield (','.join(map(str, headers)))

    for line in read_file(key_obj, conf, user_period, adm1_code, adm2_code):
        yield line


def read_file(f, user_conf, user_period, adm1_code, adm2_code):
    start_year, end_year, start_day, end_day = parse_period(user_period)
    unfinished_line = ''

    for byte in f:
        byte = unfinished_line + byte
        # split on whatever, or use a regex with re.split()
        lines = byte.split('\n')
        unfinished_line = lines.pop()
        for line in lines:

            # -71.062875,-8.051875,3,2015,216,BRA,1,21,confirm
            # filter output
            split = line.split(",")

            conf = split[2]

            adm1 = split[6]
            adm2 = split[7]

            # get list of adm1, adm2
            adm1_adm2 = [x for x in [adm1_code, adm2_code] if x is not None]

            # make dict of len
            # if length is 0- return the entire line.
            adm1_adm2_dict = {0: line, 1: adm1, 2: [adm1, adm2]}
            user_dict = {0: line, 1: adm1_code, 2: [adm1_code, adm2_code]}

            # match the line of text with user input
            len_input = len(adm1_adm2)
           
            year = int(split[3])
            day = int(split[4])

            full_yrs = []
            for yr in range(start_year + 1, end_year):
                full_yrs.append(yr)

            if year in full_yrs or (day >= start_day and year == start_year) and (day <= end_day and year == end_year):
                    if adm1_adm2_dict[len_input] == user_dict[len_input]:
                        # print type(user_conf)
                        # print user_conf
                        if user_conf:
                            # print 'conf is yes'
                            if conf == '3':
                                yield line
                        else:
                            # print 'confirm is no'
                            yield line


def iter_all_rows(bucket, conf, user_period, iso, adm1_code=None, adm2_code=None):
    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket(bucket)

    headers = ['longitude', 'latitude', 'confidence', 'year', 'julian_day', 'iso', 'adm1', 'adm2',
               'confidence_text']
    yield (','.join(map(str, headers)))

    for item in iterate_bucket_items(bucket, iso):
        key_obj = bucket_obj.lookup(item['Key'])

        # filter lines then yield them
        for line in read_file(key_obj, conf, user_period, adm1_code, adm2_code):
            yield line


# https://stackoverflow.com/a/44238708/4355916
def iterate_bucket_items(bucket, iso):
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')
    prefix = 'alerts-tsv/temp/glad-by-state/{}'.format(iso)

    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in page_iterator:
        for item in page['Contents']:
            yield item


def iso_download(request, iso, adm1_code=None, adm2_code=None):
    bucket = 'gfw2-data'

    # we should use our util.get_query_params() here or something
    # period should be validated the same way in this service
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    user_period = request.args.get('period', '2015-01-01,{}'.format(today))

    conf = request.args.get('gladConfirmOnly', False)

    if conf in ['False', 'FALSE', 'false', False]:

        conf = False
    else:

        conf = True

    # if adm1, could have adm1 or adm2
    if adm1_code:
        folder = 'alerts-tsv/temp/glad-by-state/{}'.format(iso)
        query_id = '{}_{}'.format(iso, adm1_code)
        return download_csv(bucket, folder, query_id, conf, user_period, adm1_code, adm2_code)

    else:
        return iter_all_rows(bucket, conf, user_period, iso)

