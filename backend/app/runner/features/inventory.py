import re
from pathlib import Path

from playwright.sync_api import Page

from app.runner.step_runner import run_step
from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    click_quick_action,
    click_view_output_in_latest_message,
    goto_left_nav_icon,
    wait_for_agent_response_complete,
    wait_for_user_query_echo,
    wait_half_min,
)


def _inventory_run_query(page: Page, out_dir: Path, query_button_text: str, label_prefix: str) -> None:
    run_step(page, out_dir, label=f"{label_prefix}_01_click_quick_action", fn=lambda: click_quick_action(page, query_button_text))
    run_step(page, out_dir, label=f"{label_prefix}_02_wait_user_query_echo", fn=lambda: wait_for_user_query_echo(page, query_button_text, timeout=30_000))
    run_step(page, out_dir, label=f"{label_prefix}_03_wait_agent_response_complete", fn=lambda: wait_for_agent_response_complete(page, timeout=180_000))
    run_step(page, out_dir, label=f"{label_prefix}_04_click_view_output", fn=lambda: click_view_output_in_latest_message(page, timeout=180_000))

    run_step(page, out_dir, label=f"{label_prefix}_05_wait_view_result", fn=lambda: wait_half_min(page, f"Inventory output for: {query_button_text}"))

    close_btn = page.get_by_role("button", name=re.compile(r"close", re.I)).last
    run_step(page, out_dir, label=f"{label_prefix}_06_wait_close_visible", fn=lambda: close_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label=f"{label_prefix}_07_click_close", fn=lambda: close_btn.click(timeout=DEFAULT_TIMEOUT))


def run_inventory(page: Page, out_dir: Path) -> None:
    run_step(page, out_dir, label="inventory_01_goto_nav", fn=lambda: goto_left_nav_icon(page, "lucide-package"))
    run_step(page, out_dir, label="inventory_02_wait_url", fn=lambda: page.wait_for_url(re.compile(r"/inventorymanagement", re.I), timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="inventory_03_pause", fn=lambda: page.wait_for_timeout(1200))

    _inventory_run_query(page, out_dir, "Show me all EC2 instances", label_prefix="inventory_q1_ec2_instances")
    run_step(page, out_dir, label="inventory_04_new_session_1", fn=lambda: page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="inventory_05_pause", fn=lambda: page.wait_for_timeout(800))

    _inventory_run_query(page, out_dir, "List all S3 buckets", label_prefix="inventory_q2_s3_buckets")
    run_step(page, out_dir, label="inventory_06_new_session_2", fn=lambda: page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="inventory_07_pause", fn=lambda: page.wait_for_timeout(800))

    _inventory_run_query(page, out_dir, "Show EC2 servers in production", label_prefix="inventory_q3_ec2_prod")
    run_step(page, out_dir, label="inventory_08_wait_after_feature", fn=lambda: wait_half_min(page, "After Inventory Management (view result)"))