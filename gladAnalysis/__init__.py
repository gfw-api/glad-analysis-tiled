"""The API MODULE"""

import logging
import os

import RWAPIMicroservicePython
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from gladAnalysis.config import SETTINGS
from gladAnalysis.routes.api import error
from gladAnalysis.routes.api.v1 import glad_analysis_endpoints, custom_geom_endpoints
from gladAnalysis.utils.files import load_config_json
from gladAnalysis.utils.scheduler import sync_db

logging.basicConfig(
    level=SETTINGS.get('logging', {}).get('level'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y%m%d-%H:%M%p',
)

sched = BackgroundScheduler(timezone="UTC", daemon=True)
sched.add_job(sync_db, 'interval', minutes=5)
sched.start()

# Flask App
app = Flask(__name__)

# Routing
app.url_map.strict_slashes = False
app.register_blueprint(glad_analysis_endpoints, url_prefix='/api/v1/glad-alerts-athena')
app.register_blueprint(custom_geom_endpoints, url_prefix='/api/v1/glad-alerts-athena')
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

# CT
info = load_config_json('register')
swagger = load_config_json('swagger')
RWAPIMicroservicePython.register(
    app=app,
    gateway_url=os.getenv('GATEWAY_URL'),
    token=os.getenv('MICROSERVICE_TOKEN'),
)


@app.errorhandler(403)
def forbidden(e):
    return error(status=403, detail='Forbidden')


@app.errorhandler(404)
def page_not_found(e):
    return error(status=404, detail='Not Found')


@app.errorhandler(405)
def method_not_allowed(e):
    return error(status=405, detail='Method Not Allowed')


@app.errorhandler(410)
def gone(e):
    return error(status=410, detail='Gone')


@app.errorhandler(500)
def internal_server_error(e):
    return error(status=500, detail='Internal Server Error')
