"""Main Script"""

import os
from gladAnalysis import app


#https://stackoverflow.com/questions/1661275/
import logging
import boto3
logging.getLogger('boto').setLevel(logging.CRITICAL)
boto3.set_stream_logger('boto3.resources', logging.ERROR)


# This is only used when running locally. When running live, Gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT')),
        debug=os.getenv('DEBUG') == 'True',
        threaded=True
    )
