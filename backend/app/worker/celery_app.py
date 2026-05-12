import os
import logging
from celery import Celery
from app.config import REDIS_URL

logger = logging.getLogger(__name__)

celery = Celery(
    "portal_e2e",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"],  # <-- IMPORTANT
)

celery.conf.task_track_started = True
celery.conf.result_expires = 3600

# Windows compatibility: use solo pool (single process, no multiprocessing)
if os.name == "nt":
    logger.info("[CELERY] Running on Windows, using solo pool")
    celery.conf.worker_pool = "solo"
    celery.conf.worker_prefetch_multiplier = 1
else:
    # Linux/Mac can use prefork or threads
    celery.conf.worker_pool = "prefork"
    celery.conf.worker_max_tasks_per_child = 1000

logger.info(f"[CELERY] Initialized with broker={REDIS_URL}")