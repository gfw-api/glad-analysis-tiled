from flask import Flask
from flask import Response
from gladAnalysis.services import download_service
app = Flask(__name__)

import boto3
from boto.s3.connection import S3Connection

conn = S3Connection()


def iter_all_rows(bucket, iso, adm1_code, adm2_code, alert_year):
    s3_conn = S3Connection()
    bucket_obj = s3_conn.get_bucket(bucket)

    #
    # alert_year = '2017'
    for item in iterate_bucket_items(bucket, iso):
        key_obj = bucket_obj.lookup(item['Key'])

        # filter lines then yield them
        for line in download_service.read_file(key_obj, alert_year, adm1_code, adm2_code):
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
