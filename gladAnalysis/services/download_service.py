from flask import Flask
from flask import Response
from flask import jsonify
app = Flask(__name__)
from shapely.geometry import shape

import boto3

from boto.s3.connection import S3Connection
import datetime
from gladAnalysis.middleware import AthenaWaiter
conn = S3Connection()


def download_csv(bucket, path, query_id, start_year, end_year, start_day, end_day, adm1_code=None, adm2_code=None):
    # read and filter a single csv

    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket(bucket)

    result_key = '{0}/{1}.csv'.format(path, query_id)
    key_obj = bucket_obj.lookup(result_key)

    for line in read_file(key_obj, start_year, end_year, start_day, end_day, adm1_code, adm2_code):
        yield line


def read_file(f, start_year, end_year, start_day, end_day, adm1_code=None, adm2_code=None):
    unfinished_line = ''

    for byte in f:
        byte = unfinished_line + byte
        # split on whatever, or use a regex with re.split()
        lines = byte.split('\n')
        unfinished_line = lines.pop()
        for line in lines:

            # -71.062875,-8.051875,3,2015,216,BRA,1,21,confirmed
            # filter output
            split = line.split(",")

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

            if year in full_yrs or (day >= start_day and year == start_year) or (day <= end_day and year == end_year):
                if adm1_adm2_dict[len_input] == user_dict[len_input]:
                    yield line
   
