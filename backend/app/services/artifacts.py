from __future__ import annotations

from pathlib import Path
from typing import Dict

from playwright.sync_api import Page


def save_artifacts(page: Page, out_dir: Path) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = out_dir / "screenshot.png"
    html_path = out_dir / "page.html"

    page.screenshot(path=str(screenshot_path), full_page=True)
    html_path.write_text(page.content(), encoding="utf-8")

    return {
        "screenshot": str(screenshot_path),
        "html": str(html_path),
    }