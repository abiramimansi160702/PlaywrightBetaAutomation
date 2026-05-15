from __future__ import annotations

from pathlib import Path
from typing import Callable, TypeVar

from playwright.sync_api import Page

from app.services.artifacts import save_artifacts

T = TypeVar("T")


def run_step(page: Page, out_dir: Path, *, label: str, fn: Callable[[], T]) -> T:
    """
    Run one micro-step.
    If it raises, capture artifacts in out_dir and re-raise.
    """
    try:
        return fn()
    except Exception:
        save_artifacts(page=page, out_dir=out_dir, label=label)
        raise