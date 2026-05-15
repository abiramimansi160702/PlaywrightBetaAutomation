from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from playwright.sync_api import sync_playwright, Page

from app.config import ARTIFACTS_DIR, DEFAULT_TIMEOUT_MS, HEADLESS
from app.services.artifacts import save_artifacts
from app.services.store import get_run, set_run

from app.runner.features.aiops import run_aiops
from app.runner.features.finops import run_finops
from app.runner.features.inventory import run_inventory
from app.runner.features.log_analytics import run_log_analytics
from app.runner.features.os_management import run_os_management

from app.runner.helpers import login, select_workspace

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_run(run_id: str) -> Optional[Dict[str, Any]]:
    return get_run(run_id)


def _save_run(run_id: str, data: Dict[str, Any]) -> None:
    set_run(run_id, data)


def _set_state(run_id: str, state: str, current_feature: Optional[str] = None) -> None:
    data = _load_run(run_id)
    if not data:
        logger.error(f"[SUITE] Failed to load run {run_id} for state update")
        return
    logger.info(f"[SUITE] Setting run {run_id} state to '{state}', current_feature='{current_feature}'")
    data["state"] = state
    data["current_feature"] = current_feature
    _save_run(run_id, data)


def _update_feature(run_id: str, feature: str, patch: Dict[str, Any]) -> None:
    data = _load_run(run_id)
    if not data:
        logger.error(f"[SUITE] Failed to load run {run_id} for feature update")
        return
    for fr in data.get("features", []):
        if fr.get("feature") == feature:
            fr.update(patch)
            break
    _save_run(run_id, data)


def _artifact_dir(run_id: str, feature: str) -> Path:
    base = Path(ARTIFACTS_DIR)
    d = base / run_id / feature
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_e2e_suite(run_id: str, run_request: dict) -> None:
    logger.info(f"[SUITE] Starting E2E suite for run {run_id}")

    base_url = run_request.get("base_url")
    credentials = run_request.get("credentials", {})
    workspace = run_request.get("workspace", {})

    feature_plan: list[tuple[str, Callable[[Page, Path], None]]] = [
        ("aiops", run_aiops),
        ("finops_cost_analytics", run_finops),
        ("inventory_management", run_inventory),
        ("log_analytics_agent", run_log_analytics),
        ("os_management", run_os_management),
    ]

    _set_state(run_id, "running", current_feature=None)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MS)

        try:
            logger.info(f"[SUITE] Logging in for run {run_id}")
            login(
                page=page,
                base_url=base_url,
                email=credentials.get("email"),
                password=credentials.get("password"),
                mfa_code=credentials.get("mfa_code"),
            )

            logger.info(f"[SUITE] Selecting workspace for run {run_id}")
            select_workspace(
                page=page,
                business=workspace.get("business"),
                environment=workspace.get("environment"),
                cloud_provider=workspace.get("cloud_provider"),
                account=workspace.get("account"),
            )

            for feature_name, fn in feature_plan:
                logger.info(f"[SUITE] Starting feature {feature_name} for run {run_id}")
                _set_state(run_id, "running", current_feature=feature_name)
                _update_feature(
                    run_id,
                    feature_name,
                    {"status": "running", "started_at": _utc_now(), "message": ""},
                )

                out_dir = _artifact_dir(run_id, feature_name)

                try:
                    logger.info(f"[SUITE] Executing feature {feature_name}")
                    fn(page, out_dir)

                    logger.info(f"[SUITE] Feature {feature_name} PASSED for run {run_id}")
                    _update_feature(
                        run_id,
                        feature_name,
                        {"status": "passed", "finished_at": _utc_now()},
                    )

                except Exception as e:
                    logger.error(f"[SUITE] Feature {feature_name} FAILED for run {run_id}: {str(e)}", exc_info=True)

                    # Optional: boundary capture (micro-step capture will already have happened)
                    artifacts = save_artifacts(page=page, out_dir=out_dir, label="feature_failed_boundary")

                    _update_feature(
                        run_id,
                        feature_name,
                        {
                            "status": "failed",
                            "message": str(e),
                            "finished_at": _utc_now(),
                            "artifacts": artifacts,
                        },
                    )

            logger.info(f"[SUITE] All features completed for run {run_id}")
            _set_state(run_id, "completed", current_feature=None)

        except Exception as e:
            logger.error(f"[SUITE] Suite failed for run {run_id}: {str(e)}", exc_info=True)
            _set_state(run_id, "failed", current_feature=None)

            out_dir = _artifact_dir(run_id, "suite_failure")
            artifacts = save_artifacts(page=page, out_dir=out_dir, label="suite_failed")

            data = _load_run(run_id)
            if data:
                data["error_message"] = str(e)
                data["artifacts"] = artifacts
                _save_run(run_id, data)
            raise

        finally:
            logger.info(f"[SUITE] Closing browser for run {run_id}")
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass

    data = _load_run(run_id)
    if data:
        data["finished_at"] = _utc_now()
        _save_run(run_id, data)
        logger.info(f"[SUITE] Suite execution complete for run {run_id}")