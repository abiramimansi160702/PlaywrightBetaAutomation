import re
import time
from pathlib import Path

from playwright.sync_api import Page

from app.runner.step_runner import run_step
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


def run_aiops(page: Page, out_dir: Path) -> None:
    run_step(page, out_dir, label="aiops_01_goto_nav", fn=lambda: goto_left_nav_icon(page, "lucide-zap"))
    run_step(page, out_dir, label="aiops_02_pause", fn=lambda: page.wait_for_timeout(500))

    run_step(
        page,
        out_dir,
        label="aiops_03_click_create_ec2_instance",
        fn=lambda: page.get_by_role("button", name=re.compile(r"create ec2 instance", re.I)).click(timeout=DEFAULT_TIMEOUT),
    )

    run_step(page, out_dir, label="aiops_04_select_region", fn=lambda: click_chip(page, "ap-south-1 (Mumbai)"))
    run_step(page, out_dir, label="aiops_05_select_vcpu", fn=lambda: click_chip(page, "2 vCPU"))
    run_step(page, out_dir, label="aiops_06_select_instance_type", fn=lambda: click_chip(page, "m5.large | 8.0 GiB | $0.101/hr"))
    run_step(page, out_dir, label="aiops_07_select_os", fn=lambda: click_chip(page, "Ubuntu"))

    run_step(page, out_dir, label="aiops_08_wait_ami_prompt", fn=lambda: wait_for_prompt(page, r"please provide the ami id"))
    run_step(page, out_dir, label="aiops_09_open_ami_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_10_pick_ami", fn=lambda: pick_from_modal_by_name_text(page, "ubuntu24-latest"))

    run_step(page, out_dir, label="aiops_11_wait_vpc_prompt", fn=lambda: wait_for_prompt(page, r"please provide the vpc id"))
    run_step(page, out_dir, label="aiops_12_open_vpc_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_13_pick_vpc", fn=lambda: pick_from_modal_by_name_text(page, "acme-prod-vm-vpc"))

    run_step(page, out_dir, label="aiops_14_wait_subnet_prompt", fn=lambda: wait_for_prompt(page, r"please provide the subnet id"))
    run_step(page, out_dir, label="aiops_15_open_subnet_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_16_pick_subnet", fn=lambda: pick_from_modal_by_name_text(page, "acme-prod-vm-sub1"))

    run_step(page, out_dir, label="aiops_17_wait_sg_prompt", fn=lambda: wait_for_prompt(page, r"please provide the security group id"))
    run_step(page, out_dir, label="aiops_18_open_sg_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_19_pick_sg", fn=lambda: pick_from_modal_by_name_text(page, "acme-prod-vm-sg1"))

    run_step(page, out_dir, label="aiops_20_wait_keypair_prompt", fn=lambda: wait_for_prompt(page, r"please provide the key pair"))
    run_step(page, out_dir, label="aiops_21_open_keypair_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_22_pick_keypair", fn=lambda: pick_from_modal_by_name_text(page, "linux-key"))

    run_step(page, out_dir, label="aiops_23_wait_projectowner_tag_prompt", fn=lambda: wait_for_prompt(page, r"projectowner tag"))
    run_step(
        page,
        out_dir,
        label="aiops_24_select_projectowner_user5",
        fn=lambda: page.get_by_role("button", name=re.compile(r"user5", re.I)).click(timeout=DEFAULT_TIMEOUT),
    )

    run_step(page, out_dir, label="aiops_25_wait_application_tag_prompt", fn=lambda: wait_for_prompt(page, r"application tag"))
    run_step(
        page,
        out_dir,
        label="aiops_26_select_application_frontend",
        fn=lambda: page.get_by_role("button", name=re.compile(r"frontend", re.I)).click(timeout=DEFAULT_TIMEOUT),
    )

    run_step(page, out_dir, label="aiops_27_wait_name_tag_prompt", fn=lambda: wait_for_prompt(page, r"name tag"))
    instance_name = f"prod-frontend-user5-{time.strftime('%y%m%d-%H%M%S')}-ec2"
    run_step(page, out_dir, label="aiops_28_fill_instance_name", fn=lambda: fill_instance_name_and_send(page, instance_name))

    run_step(page, out_dir, label="aiops_29_wait_kms_prompt", fn=lambda: wait_for_prompt(page, r"please provide the kms_key|kms key"))
    run_step(page, out_dir, label="aiops_30_open_kms_modal", fn=lambda: open_suggestions_modal(page))
    run_step(page, out_dir, label="aiops_31_pick_kms", fn=lambda: pick_from_modal_by_name_text(page, "alias/MytestKMSkey"))

    run_step(page, out_dir, label="aiops_32_assert_kms_and_success", fn=lambda: assert_kms_and_success(page))
    run_step(page, out_dir, label="aiops_33_wait_view_result", fn=lambda: wait_half_min(page, "After AIOps EC2 creation (view result)"))