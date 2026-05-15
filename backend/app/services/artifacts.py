from __future__ import annotations

import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from playwright.sync_api import Page


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")


def _safe_slug(value: str, max_len: int = 100) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = "artifact"
    return value[:max_len]


def save_artifacts(
    page: Page,
    out_dir: Path,
    *,
    label: Optional[str] = None,
    full_page: bool = True,
) -> Dict[str, str]:
    """
    Best-effort artifact capture. Never raises.

    - Writes unique filenames per call
    - Attempts screenshot + HTML
    - If page/browser is closed, writes artifact_error.txt explaining the failure
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = _utc_stamp()
    prefix = f"{stamp}_{_safe_slug(label)}" if label else stamp

    screenshot_path = out_dir / f"{prefix}_screenshot.png"
    html_path = out_dir / f"{prefix}_page.html"
    error_path = out_dir / f"{prefix}_artifact_error.txt"

    written: Dict[str, str] = {}

    # Screenshot
    try:
        page.screenshot(path=str(screenshot_path), full_page=full_page)
        written["screenshot"] = str(screenshot_path)
    except Exception as e:
        error_path.write_text(
            "Failed to capture screenshot.\n\n"
            f"Exception: {type(e).__name__}: {e}\n\n"
            "Traceback:\n"
            f"{traceback.format_exc()}",
            encoding="utf-8",
        )
        written["artifact_error"] = str(error_path)

    # HTML
    try:
        html_path.write_text(page.content(), encoding="utf-8")
        written["html"] = str(html_path)
    except Exception as e:
        prior = ""
        if error_path.exists():
            try:
                prior = error_path.read_text(encoding="utf-8")
            except Exception:
                prior = ""
        error_path.write_text(
            ((prior + "\n\n---\n\n") if prior else "")
            + "Failed to capture HTML.\n\n"
            f"Exception: {type(e).__name__}: {e}\n\n"
            "Traceback:\n"
            f"{traceback.format_exc()}",
            encoding="utf-8",
        )
        written["artifact_error"] = str(error_path)

    # Page info (extra context)
    try:
        info_path = out_dir / f"{prefix}_page_info.txt"
        try:
            url = page.url
        except Exception:
            url = ""
        try:
            title = page.title()
        except Exception:
            title = ""
        info_path.write_text(
            f"timestamp_utc: {stamp}\nlabel: {label or ''}\nurl: {url}\ntitle: {title}\n",
            encoding="utf-8",
        )
        written["page_info"] = str(info_path)
    except Exception:
        pass

    return written