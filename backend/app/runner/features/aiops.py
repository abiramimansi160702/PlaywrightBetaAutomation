import re
import time
from playwright.sync_api import Page

from app.runner.helpers import (
    DEFAULT_TIMEOUT,
    assert_kms_and_success,
    click_chip,
    fill_instance_name_and_send,
    goto_left_nav_icon,
    open_suggestions_modal,
    pick_from_modal_by_name_text,
    wait_for_prompt,
    wait_half_min,
)


def run_aiops(page: Page) -> None:
    print("AIOps: Starting AIOps test")
    goto_left_nav_icon(page, "lucide-zap")  # AIOps Agent
    page.wait_for_timeout(500)
    print("AIOps: Navigated to AIOps")

    page.get_by_role("button", name=re.compile(r"create ec2 instance", re.I)).click(timeout=DEFAULT_TIMEOUT)
    print("AIOps: Clicked create EC2 button")

    click_chip(page, "ap-south-1 (Mumbai)")
    print("AIOps: Selected region")
    click_chip(page, "2 vCPU")
    print("AIOps: Selected vCPU")
    click_chip(page, "m5.large | 8.0 GiB | $0.101/hr")
    print("AIOps: Selected instance type")
    click_chip(page, "Ubuntu")
    print("AIOps: Selected OS")

    wait_for_prompt(page, r"please provide the ami id")
    print("AIOps: Waited for AMI prompt")
    open_suggestions_modal(page)
    print("AIOps: Opened suggestions modal for AMI")
    pick_from_modal_by_name_text(page, "ubuntu24-latest")
    print("AIOps: Picked AMI")

    wait_for_prompt(page, r"please provide the vpc id")
    print("AIOps: Waited for VPC prompt")
    open_suggestions_modal(page)
    print("AIOps: Opened suggestions modal for VPC")
    pick_from_modal_by_name_text(page, "acme-prod-vm-vpc")
    print("AIOps: Picked VPC")

    wait_for_prompt(page, r"please provide the subnet id")
    print("AIOps: Waited for subnet prompt")
    open_suggestions_modal(page)
    print("AIOps: Opened suggestions modal for subnet")
    pick_from_modal_by_name_text(page, "acme-prod-vm-sub1")
    print("AIOps: Picked subnet")

    wait_for_prompt(page, r"please provide the security group id")
    print("AIOps: Waited for SG prompt")
    open_suggestions_modal(page)
    print("AIOps: Opened suggestions modal for SG")
    pick_from_modal_by_name_text(page, "acme-prod-vm-sg1")
    print("AIOps: Picked SG")

    wait_for_prompt(page, r"please provide the key pair")
    print("AIOps: Waited for key pair prompt")
    open_suggestions_modal(page)
    print("AIOps: Opened suggestions modal for key pair")
    pick_from_modal_by_name_text(page, "linux-key")
    print("AIOps: Picked key pair")

    wait_for_prompt(page, r"projectowner tag")
    print("AIOps: Waited for tag prompt")
    page.get_by_role("button", name=re.compile(r"user5", re.I)).click(timeout=DEFAULT_TIMEOUT)
    print("AIOps: Selected tag, test completed")

    wait_for_prompt(page, r"application tag")
    page.get_by_role("button", name=re.compile(r"frontend", re.I)).click(timeout=DEFAULT_TIMEOUT)

    wait_for_prompt(page, r"name tag")
    instance_name = f"prod-frontend-user5-{time.strftime('%y%m%d-%H%M%S')}-ec2"
    fill_instance_name_and_send(page, instance_name)

    wait_for_prompt(page, r"please provide the kms_key|kms key")
    open_suggestions_modal(page)
    pick_from_modal_by_name_text(page, "alias/MytestKMSkey")

    assert_kms_and_success(page)
    wait_half_min(page, "After AIOps EC2 creation (view result)")