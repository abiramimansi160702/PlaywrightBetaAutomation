import re
from pathlib import Path

from playwright.sync_api import Page

from app.runner.step_runner import run_step
from app.services.artifacts import save_artifacts
from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    click_quick_action,
    goto_left_nav_icon,
    open_os_instance_picker,
    wait_half_min,
    wait_os_instances_or_empty,
)


def run_os_management(page: Page, out_dir: Path) -> None:
    run_step(page, out_dir, label="osmgmt_01_goto_nav", fn=lambda: goto_left_nav_icon(page, "lucide-app-window-mac"))
    run_step(page, out_dir, label="osmgmt_02_pause", fn=lambda: page.wait_for_timeout(500))
    run_step(page, out_dir, label="osmgmt_03_wait_url", fn=lambda: page.wait_for_url(re.compile(r"/osmanagement", re.I), timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="osmgmt_04_pause", fn=lambda: page.wait_for_timeout(1200))

    run_step(page, out_dir, label="osmgmt_05_open_instance_picker", fn=lambda: open_os_instance_picker(page))

    # wait_os_instances_or_empty returns (modal, count). If it throws, run_step captures.
    modal, count = run_step(page, out_dir, label="osmgmt_06_wait_instances_or_empty", fn=lambda: wait_os_instances_or_empty(page, timeout=60_000))

    if count == 0:
        # Capture evidence and skip
        save_artifacts(page=page, out_dir=out_dir, label="osmgmt_no_instances_available")
        try:
            modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT)
        except Exception:
            pass
        return

    connected = False
    connect_btns = modal.get_by_role("button", name=re.compile(r"connect", re.I))

    for i in range(count):
        run_step(page, out_dir, label=f"osmgmt_07_click_connect_{i}", fn=lambda i=i: connect_btns.nth(i).click(timeout=DEFAULT_TIMEOUT))

        conn_modal = page.locator("div[role='dialog']", has_text=re.compile(r"choose connection type", re.I))
        run_step(page, out_dir, label=f"osmgmt_08_wait_conn_modal_{i}", fn=lambda: conn_modal.wait_for(state="visible", timeout=DEFAULT_TIMEOUT))

        public_ip = conn_modal.get_by_role("button", name=re.compile(r"public ip", re.I))
        try:
            if public_ip.count() > 0 and public_ip.first.is_enabled():
                run_step(page, out_dir, label=f"osmgmt_09_click_public_ip_{i}", fn=lambda: public_ip.first.click(timeout=DEFAULT_TIMEOUT))
                run_step(page, out_dir, label=f"osmgmt_10_pause_after_connect_{i}", fn=lambda: page.wait_for_timeout(1500))
                connected = True
                break
        except Exception:
            # If checking availability fails due to closure, capture will happen in the next failing run_step,
            # but we can still capture here explicitly.
            save_artifacts(page=page, out_dir=out_dir, label=f"osmgmt_public_ip_check_failed_{i}")
            raise

        # Close connection modal (X)
        run_step(
            page,
            out_dir,
            label=f"osmgmt_11_close_conn_modal_{i}",
            fn=lambda: conn_modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT),
        )
        run_step(page, out_dir, label=f"osmgmt_12_pause_after_close_{i}", fn=lambda: page.wait_for_timeout(400))

    # Close instance picker modal if still visible
    try:
        if modal.is_visible():
            run_step(
                page,
                out_dir,
                label="osmgmt_13_close_instance_picker",
                fn=lambda: modal.locator("button").filter(has=page.locator("svg")).last.click(timeout=DEFAULT_TIMEOUT),
            )
    except Exception:
        pass

    if not connected:
        save_artifacts(page=page, out_dir=out_dir, label="osmgmt_no_public_ip_connection_available")
        return

    run_step(page, out_dir, label="osmgmt_14_quick_action_disk_space", fn=lambda: click_quick_action(page, "Check disk space"))
    run_step(page, out_dir, label="osmgmt_15_wait_result_disk_space", fn=lambda: wait_half_min(page, "OS Mgmt result (disk space)"))

    run_step(page, out_dir, label="osmgmt_16_new_session", fn=lambda: page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="osmgmt_17_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(page, out_dir, label="osmgmt_18_quick_action_installed_packages", fn=lambda: click_quick_action(page, "List installed packages"))
    run_step(page, out_dir, label="osmgmt_19_wait_result_installed_packages", fn=lambda: wait_half_min(page, "OS Mgmt result (installed packages)"))

    run_step(page, out_dir, label="osmgmt_20_new_session", fn=lambda: page.get_by_role("button", name=re.compile(r"new session", re.I)).click(timeout=DEFAULT_TIMEOUT))
    run_step(page, out_dir, label="osmgmt_21_pause", fn=lambda: page.wait_for_timeout(800))

    run_step(page, out_dir, label="osmgmt_22_quick_action_memory_usage", fn=lambda: click_quick_action(page, "Check memory usage"))
    run_step(page, out_dir, label="osmgmt_23_wait_result_memory_usage", fn=lambda: wait_half_min(page, "OS Mgmt result (memory usage)"))