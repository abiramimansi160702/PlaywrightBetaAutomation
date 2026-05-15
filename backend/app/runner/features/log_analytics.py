import re
from pathlib import Path

from playwright.sync_api import Page

from app.runner.step_runner import run_step
from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    click_quick_action,
    goto_left_nav_icon,
    wait_for_thinking_to_finish,
    wait_half_min,
)


def run_log_analytics(page: Page, out_dir: Path) -> None:
    run_step(page, out_dir, label="loganalytics_01_goto_nav", fn=lambda: goto_left_nav_icon(page, "lucide-scroll-text"))
    run_step(page, out_dir, label="loganalytics_02_pause", fn=lambda: page.wait_for_timeout(500))
    run_step(page, out_dir, label="loganalytics_03_wait_url", fn=lambda: page.wait_for_url(re.compile(r"/logAnalytics", re.I), timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="loganalytics_04_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(page, out_dir, label="loganalytics_05_quick_action_stopped_terminated", fn=lambda: click_quick_action(page, "Who stopped or terminated EC2"))
    run_step(page, out_dir, label="loganalytics_06_wait_thinking_finish_1", fn=lambda: wait_for_thinking_to_finish(page, timeout=180_000))
    run_step(page, out_dir, label="loganalytics_07_wait_view_result_1", fn=lambda: wait_half_min(page, "Log Analytics result (stopped/terminated EC2)"))

    run_step(page, out_dir, label="loganalytics_08_new_session", fn=lambda: page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="loganalytics_09_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(page, out_dir, label="loganalytics_10_quick_action_modified_sg", fn=lambda: click_quick_action(page, "Who modified security groups"))
    run_step(page, out_dir, label="loganalytics_11_wait_thinking_finish_2", fn=lambda: wait_for_thinking_to_finish(page, timeout=180_000))
    run_step(page, out_dir, label="loganalytics_12_wait_view_result_2", fn=lambda: wait_half_min(page, "Log Analytics result (modified security groups)"))