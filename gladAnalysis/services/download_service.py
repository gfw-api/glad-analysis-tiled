# from flask import Flask
# from flask import Response
# from flask import jsonify
# app = Flask(__name__)
# from shapely.geometry import shape
#
# import boto3
#
# from boto.s3.connection import S3Connection
#
# from gladAnalysis.middleware import AthenaWaiter
# conn = S3Connection()
#

def test_me():

    return {'this': 'ok'}


def download_csv(bucket, path, query_id, alert_year, adm1_code=None, adm2_code=None):

    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket(bucket)

    result_key = '{0}/{1}.csv'.format(path, query_id)
    key_obj = bucket_obj.lookup(result_key)

    for line in read_file(key_obj, alert_year, adm1_code, adm2_code):
        yield line


def read_file(f, alert_year, adm1_code=None, adm2_code=None):
    unfinished_line = ''

    for byte in f:
        byte = unfinished_line + byte
        # split on whatever, or use a regex with re.split()
        lines = byte.split('\n')
        unfinished_line = lines.pop()
        for line in lines:

            # filter output
            split = line.split(",")

            year = split[3]
            adm1 = split[6]
            adm2 = split[7]

            if year == alert_year and adm1 == adm1_code and adm2 == adm2_code:

                yield line


