import json
import logging
from typing import Any, Dict, Optional

import redis
from app.config import REDIS_URL

logger = logging.getLogger(__name__)

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

RUN_KEY_PREFIX = "portal-e2e:run:"


def _key(run_id: str) -> str:
    return f"{RUN_KEY_PREFIX}{run_id}"


def set_run(run_id: str, payload: Dict[str, Any]) -> None:
    key = _key(run_id)
    logger.info(f"[STORE] Setting run {run_id}: state={payload.get('state')}, current_feature={payload.get('current_feature')}")
    r.set(key, json.dumps(payload))
    logger.info(f"[STORE] Run {run_id} saved to Redis")


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    raw = r.get(_key(run_id))
    if not raw:
        logger.warning(f"[STORE] Run {run_id} not found in Redis")
        return None
    data = json.loads(raw)
    logger.debug(f"[STORE] Retrieved run {run_id}: state={data.get('state')}, current_feature={data.get('current_feature')}")
    return data