import re
from playwright.sync_api import Page

from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    click_quick_action,
    goto_left_nav_icon,
    open_os_instance_picker,
    wait_half_min,
    wait_os_instances_or_empty,
)


def run_os_management(page: Page) -> None:
    goto_left_nav_icon(page, "lucide-app-window-mac")  # OS Management
    page.wait_for_timeout(500)
    page.wait_for_url(re.compile(r"/osmanagement", re.I), timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(1200)

    open_os_instance_picker(page)
    modal, count = wait_os_instances_or_empty(page, timeout=60_000)

    if count == 0:
        print("OS Management: No instances available for current workspace/account. Skipping OS tests.")
        modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT)
        return

    print(f"OS Management: found {count} instances; trying Public IP connect...")

    connected = False
    connect_btns = modal.get_by_role("button", name=re.compile(r"connect", re.I))
    for i in range(count):
        connect_btns.nth(i).click(timeout=DEFAULT_TIMEOUT)

        conn_modal = page.locator("div[role='dialog']", has_text=re.compile(r"choose connection type", re.I))
        conn_modal.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)

        public_ip = conn_modal.get_by_role("button", name=re.compile(r"public ip", re.I))
        if public_ip.count() > 0 and public_ip.first.is_enabled():
            public_ip.first.click(timeout=DEFAULT_TIMEOUT)
            page.wait_for_timeout(1500)
            connected = True
            break

        conn_modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT)
        page.wait_for_timeout(400)

    try:
        if modal.is_visible():
            modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT)
    except Exception:
        pass

    if not connected:
        print("OS Management: Instances exist, but none supports Public IP. Skipping OS tests.")
        return

    click_quick_action(page, "Check disk space")
    wait_half_min(page, "OS Mgmt result (disk space)")

    page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    click_quick_action(page, "List installed packages")
    wait_half_min(page, "OS Mgmt result (installed packages)")

    page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(800)

    click_quick_action(page, "Check memory usage")
    wait_half_min(page, "OS Mgmt result (memory usage)")