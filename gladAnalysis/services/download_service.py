from flask import Flask
from flask import Response
from flask import jsonify
app = Flask(__name__)
from shapely.geometry import shape

import boto3

from boto.s3.connection import S3Connection

from gladAnalysis.middleware import AthenaWaiter
conn = S3Connection()


def test_me():

    return {'this': 'ok'}


def download_csv(bucket, path, query_id):

    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket('gfw2-data')

    # wait for response
    result_key = '{1}/{2}.csv'.format(bucket, path, query_id)

    waiter = AthenaWaiter(max_tries=1000)
    waiter.wait(
        bucket='gfw2-data',
        key=result_key,
        query_id=query_id
    )
    # get result
    key_obj = bucket_obj.lookup(result_key)

    for line in read_file(key_obj):
        yield line


def read_file(f):
    unfinished_line = ''
    for byte in f:
        byte = unfinished_line + byte
        # split on whatever, or use a regex with re.split()
        lines = byte.split('\n')
        unfinished_line = lines.pop()
        for line in lines:
            yield line
