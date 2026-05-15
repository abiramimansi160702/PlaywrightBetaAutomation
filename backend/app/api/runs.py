from datetime import datetime, timezone
import uuid
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import RunE2ERequest
from app.services.store import set_run, get_run
from app.worker.tasks import run_e2e_suite_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["runs"])

FEATURES = [
    "aiops",
    "finops_cost_analytics",
    "inventory_management",
    "log_analytics_agent",
    "os_management",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_blank(v) -> bool:
    return v is None or str(v).strip() == ""


@router.post("/e2e")
def create_e2e_run(req: RunE2ERequest):
    # ---- NEW: Validate workspace fields before creating/queuing a run ----
    ws = getattr(req, "workspace", None)
    missing = []

    if ws is None:
        missing.append("workspace")
    else:
        # These attribute names assume your RunE2ERequest.workspace has these fields.
        # If your schema uses different names, tell me and I'll adjust.
        if _is_blank(getattr(ws, "business", None)):
            missing.append("workspace.business")
        if _is_blank(getattr(ws, "environment", None)):
            missing.append("workspace.environment")
        if _is_blank(getattr(ws, "cloud_provider", None)):
            missing.append("workspace.cloud_provider")
        if _is_blank(getattr(ws, "account", None)):
            missing.append("workspace.account")

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Workspace values are required to start the E2E run.",
                "missing_fields": missing,
            },
        )
    # -------------------------------------------------------------------

    run_id = str(uuid.uuid4())
    logger.info(f"[API] Creating E2E run {run_id} with base_url={req.base_url}")

    payload = {
        "run_id": run_id,
        "state": "queued",
        "current_feature": None,
        "created_at": _utc_now(),
        "finished_at": None,
        "features": [
            {
                "feature": f,
                "status": "pending",
                "message": "",
                "started_at": None,
                "finished_at": None,
                "artifacts": {},
            }
            for f in FEATURES
        ],
    }
    set_run(run_id, payload)
    logger.info(f"[API] Run {run_id} saved to Redis, queuing task...")

    task = run_e2e_suite_task.delay(run_id, req.model_dump())
    logger.info(f"[API] Task queued for run {run_id}, task_id={task.id}")
    return {"run_id": run_id}


@router.get("/{run_id}")
def get_run_status(run_id: str):
    data = get_run(run_id)
    if not data:
        logger.warning(f"[API] Run {run_id} not found in Redis")
        raise HTTPException(status_code=404, detail="run_id not found")
    logger.debug(f"[API] Returning run {run_id}: state={data.get('state')}, current_feature={data.get('current_feature')}")
    return data