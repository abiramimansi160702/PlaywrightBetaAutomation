import re
from pathlib import Path

from playwright.sync_api import Page

from app.runner.step_runner import run_step
from app.runner.helpers import DEFAULT_TIMEOUT, click_quick_action, goto_left_nav_icon, wait_half_min


def run_finops(page: Page, out_dir: Path) -> None:
    run_step(
        page,
        out_dir,
        label="finops_01_goto_nav",
        fn=lambda: goto_left_nav_icon(page, "lucide-chart-no-axes-combined"),
    )
    run_step(
        page,
        out_dir,
        label="finops_02_wait_finops_url",
        fn=lambda: page.wait_for_url(re.compile(r"/finops", re.I), timeout=DEFAULT_TIMEOUT),
    )
    run_step(page, out_dir, label="finops_03_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(
        page,
        out_dir,
        label="finops_04_click_cost_analytics_tile",
        fn=lambda: page.get_by_text(re.compile(r"^Cost Analytics$", re.I)).first.click(timeout=DEFAULT_TIMEOUT),
    )

    # FIX: do NOT wait for URL navigation to "cost-analytics"
    # Instead wait for a stable UI signal that Cost Analytics is ready.
    run_step(
        page,
        out_dir,
        label="finops_05_wait_cost_analytics_ready",
        fn=lambda: page.get_by_text(
            re.compile(r"show service-wise cost breakdown", re.I)
        ).first.wait_for(timeout=20_000),
    )

    run_step(page, out_dir, label="finops_06_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(
        page,
        out_dir,
        label="finops_07_click_quick_action_show_service_wise_cost",
        fn=lambda: click_quick_action(page, "Show service-wise cost"),
    )

    run_step(
        page,
        out_dir,
        label="finops_08_wait_networkidle",
        fn=lambda: page.wait_for_load_state("networkidle", timeout=180_000),
    )
    run_step(page, out_dir, label="finops_09_pause", fn=lambda: page.wait_for_timeout(1500))
    run_step(page, out_dir, label="finops_10_wait_view_result", fn=lambda: wait_half_min(page, "FinOps: view result"))