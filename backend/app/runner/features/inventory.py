import re
from playwright.sync_api import Page

from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    click_quick_action,
    click_view_output_in_latest_message,
    goto_left_nav_icon,
    wait_for_agent_response_complete,
    wait_for_user_query_echo,
    wait_half_min,
)


def _inventory_run_query(page: Page, query_button_text: str) -> None:
    click_quick_action(page, query_button_text)
    wait_for_user_query_echo(page, query_button_text, timeout=30_000)

    wait_for_agent_response_complete(page, timeout=180_000)
    click_view_output_in_latest_message(page, timeout=180_000)

    wait_half_min(page, f"Inventory output for: {query_button_text}")

    close_btn = page.get_by_role("button", name=re.compile(r"close", re.I)).last
    close_btn.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
    close_btn.click(timeout=DEFAULT_TIMEOUT)


def run_inventory(page: Page) -> None:
    goto_left_nav_icon(page, "lucide-package")  # Inventory Management
    page.wait_for_url(re.compile(r"/inventorymanagement", re.I), timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(1200)

    _inventory_run_query(page, "Show me all EC2 instances")
    page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    _inventory_run_query(page, "List all S3 buckets")
    page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    _inventory_run_query(page, "Show EC2 servers in production")
    wait_half_min(page, "After Inventory Management (view result)")