import os
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")

DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "120000"))
HEADLESS = os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes")
POLL_INTERVAL_MS = int(os.getenv("POLL_INTERVAL_MS", "1000"))

logger.info(f"Config loaded: REDIS_URL={REDIS_URL}, ARTIFACTS_DIR={ARTIFACTS_DIR}, HEADLESS={HEADLESS}")