import re
from playwright.sync_api import Page

from app.runner.helpers import DEFAULT_TIMEOUT, click_quick_action, goto_left_nav_icon, wait_for_thinking_to_finish, wait_half_min


def run_log_analytics(page: Page) -> None:
    goto_left_nav_icon(page, "lucide-scroll-text")  # Log Analytics Agent
    page.wait_for_timeout(500)
    page.wait_for_url(re.compile(r"/logAnalytics", re.I), timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    click_quick_action(page, "Who stopped or terminated EC2")
    wait_for_thinking_to_finish(page, timeout=180_000)
    wait_half_min(page, "Log Analytics result (stopped/terminated EC2)")

    page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    click_quick_action(page, "Who modified security groups")
    wait_for_thinking_to_finish(page, timeout=180_000)
    wait_half_min(page, "Log Analytics result (modified security groups)")