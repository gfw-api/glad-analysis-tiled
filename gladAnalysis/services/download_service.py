from flask import Flask
from flask import Response
from flask import jsonify
app = Flask(__name__)
from shapely.geometry import shape

import boto3
from boto.s3.connection import S3Connection

from gladAnalysis.middleware import AthenaWaiter
conn = S3Connection()

import time


@app.route('/bra.csv')
def generate_large_csv_iso():
    def generate():
        yield 'long,lat,conf,year,day,iso,adm1,adm2,conf\n'
        for row in iter_all_rows(False):
            yield row + '\n'

    return Response(generate(), mimetype='text/csv')


@app.route('/from_geom.csv')
def generate_large_csv_geom():
    def generate():

        for row in download_csv(query_id):
            yield row + '\n'

    return Response(generate(), mimetype='text/csv')


def download_csv(query_id):
    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket('gfw2-data')

    # wait for response
    result_key = 'alerts-tsv/glad/download/{}.csv'.format(query_id)
    waiter = AthenaWaiter(max_tries=1000)
    waiter.wait(
        bucket='gfw2-data',
        key=result_key,
        query_id=query_id
    )
    # get result
    result_s3 = 'alerts-tsv/glad/download/{}.csv'.format(query_id)

    key_obj = bucket_obj.lookup(result_s3)

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
