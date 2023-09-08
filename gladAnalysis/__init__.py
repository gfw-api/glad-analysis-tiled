"""The API MODULE"""

import logging

import collections

collections.MutableMapping = collections.abc.MutableMapping
collections.Mapping = collections.abc.Mapping
collections.Iterable = collections.abc.Iterable
from apscheduler.schedulers.background import BackgroundScheduler

from gladAnalysis.config import SETTINGS
from gladAnalysis.utils.scheduler import sync_db

logging.basicConfig(
    level=SETTINGS.get("logging", {}).get("level"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y%m%d-%H:%M%p",
)

sched = BackgroundScheduler(timezone="UTC", daemon=True)
sched.add_job(sync_db, "interval", minutes=5)
sched.start()

logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
