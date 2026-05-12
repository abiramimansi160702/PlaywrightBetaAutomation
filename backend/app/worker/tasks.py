import logging
from app.worker.celery_app import celery
from app.runner.suite import run_e2e_suite

logger = logging.getLogger(__name__)

@celery.task(name="portal_e2e.run_e2e_suite", bind=True)
def run_e2e_suite_task(self, run_id: str, run_request: dict) -> None:
    """Celery task wrapper for running the E2E suite."""
    try:
        logger.info(f"[TASK] Starting task for run {run_id}")
        run_e2e_suite(run_id=run_id, run_request=run_request)
        logger.info(f"[TASK] Task completed successfully for run {run_id}")
    except Exception as e:
        logger.error(f"[TASK] Task failed for run {run_id}: {str(e)}", exc_info=True)
        raise