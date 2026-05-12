import re
from playwright.sync_api import Page

from app.runner.helpers import DEFAULT_TIMEOUT, click_quick_action, goto_left_nav_icon, wait_half_min


def run_finops(page: Page) -> None:
    goto_left_nav_icon(page, "lucide-chart-no-axes-combined")  # FinOps
    page.wait_for_url(re.compile(r"/finops", re.I), timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    page.get_by_text(re.compile(r"^Cost Analytics$", re.I)).first.click(timeout=DEFAULT_TIMEOUT)

    try:
        page.wait_for_url(re.compile(r"cost-analytics", re.I), timeout=10_000)
    except Exception:
        pass

    page.wait_for_timeout(800)

    click_quick_action(page, "Show service-wise cost")

    page.wait_for_load_state("networkidle", timeout=180_000)
    page.wait_for_timeout(1500)
    wait_half_min(page, "FinOps: view result")