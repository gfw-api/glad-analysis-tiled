import datetime
import time
import requests
import shutil
import logging
import os


def download_file(url, output):

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        with open(output, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return output


def sync_db():

    logging.debug("Sync stats.db")

    url = "http://gfw2-data.s3.amazonaws.com/forest_change/umd_landsat_alerts/prod/db/stats.db"
    output = "/opt/gladAnalysis/data/stats.db"
    temp = "/opt/gladAnalysis/data/temp.db"

    r = requests.head(url)
    meta = r.headers['last-modified']
    meta_modifiedtime = time.mktime(datetime.datetime.strptime(meta, "%a, %d %b %Y %X GMT").timetuple())

    if os.path.getmtime(output) < meta_modifiedtime:
        logging.info("Downloading latest version of stats.db")
        try:
            download_file(url, temp)
            shutil.move(temp, output)
            logging.info("Downloaded latest version of stats.db")
        except Exception as e:
            logging.error("Failed to download latest stats.db")
            logging.error(e)
    else:
        logging.debug("Local stats.db is up to date. Remote file dates: " + meta)
