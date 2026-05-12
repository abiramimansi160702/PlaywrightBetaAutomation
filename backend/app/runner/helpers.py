import re
import time
import logging
from typing import Optional, Tuple

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120_000
BREAK_MS = 30_000  # 0.5 minute


def debug_dump(page: Page, prefix: str = "failure") -> None:
    ts = time.strftime("%Y%m%d-%H%M%S")
    png = f"{prefix}-{ts}.png"
    html = f"{prefix}-{ts}.html"
    page.screenshot(path=png, full_page=True)
    with open(html, "w", encoding="utf-8") as f:
        f.write(page.content())
    print(f"Saved screenshot: {png}")
    print(f"Saved html: {html}")


def login(page: Page, base_url: str, email: str, password: str, mfa_code: Optional[str] = None) -> None:
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")

    page.get_by_role("textbox", name=re.compile(r"email", re.I)).fill(email)
    page.get_by_role("textbox", name=re.compile(r"password", re.I)).fill(password)
    page.get_by_role("button", name=re.compile(r"login", re.I)).click()

    mfa = page.get_by_role("textbox", name=re.compile(r"mfa", re.I))
    if mfa.count() > 0:
        if mfa_code is None:
            raise ValueError("MFA was prompted but no mfa_code was provided.")
        mfa.first.fill(mfa_code)
        page.get_by_role("button", name=re.compile(r"verify|continue", re.I)).click()

    page.wait_for_url(lambda url: "login" not in url, timeout=DEFAULT_TIMEOUT)


def select_workspace(
    page: Page,
    business: str,
    environment: str,
    cloud_provider: str,
    account: str,
) -> None:
    """
    Select the workspace in the portal UI.
    Assumes a workspace selector modal or dropdown exists.
    If any parameter is None or empty, skip selection.
    If the selector is not found, skip with a warning.
    """
    if not all([business, environment, cloud_provider, account]):
        logger.info("Workspace selection skipped: not all parameters provided")
        return

    try:
        # Try to find and click the workspace selector button
        selector_button = page.get_by_role("button", name=re.compile(r"select workspace|workspace|switch", re.I))
        if selector_button.count() > 0:
            selector_button.click(timeout=10000)  # Shorter timeout
            # Assume dropdowns or inputs for each field
            page.get_by_label(re.compile(r"business", re.I)).select_option(business)
            page.get_by_label(re.compile(r"environment", re.I)).select_option(environment)
            page.get_by_label(re.compile(r"cloud.provider", re.I)).select_option(cloud_provider)
            page.get_by_label(re.compile(r"account", re.I)).select_option(account)
            page.get_by_role("button", name=re.compile(r"confirm|apply|save", re.I)).click(timeout=DEFAULT_TIMEOUT)
            page.wait_for_timeout(2000)  # Wait for selection to apply
        else:
            logger.warning("Workspace selector button not found, skipping workspace selection")
    except Exception as e:
        logger.warning(f"Workspace selection failed or not available: {e}, continuing without it")

#-------- General helpers --------
def wait_half_min(page: Page, reason: str) -> None:
    print(f"Waiting 0.5 minute: {reason}")
    page.wait_for_timeout(BREAK_MS)


def goto_left_nav_icon(page: Page, icon_class: str) -> None:
    """
    Sidebar is often collapsed; clicking by text is flaky.
    Click by lucide icon class instead.
    """
    page.locator(f"nav svg.lucide.{icon_class}").first.click(timeout=DEFAULT_TIMEOUT)
    page.wait_for_timeout(600)


def click_quick_action(page: Page, label: str) -> None:
    page.get_by_role("button", name=re.compile(re.escape(label), re.I)).click(timeout=DEFAULT_TIMEOUT)


def normalize_quick_action_label(label: str) -> str:
    # In FinOps UI, quick actions end with "." but the posted user message may not.
    return label.strip().rstrip(".")

#-------- User Query helpers --------
def wait_for_user_query_echo_loose(page: Page, query_text: str, timeout: int = 30_000) -> None:
    """
    Like wait_for_user_query_echo, but tolerant of punctuation differences.
    Waits for the query text (without trailing period) to appear in chat.
    """
    q = normalize_quick_action_label(query_text)
    page.get_by_text(re.compile(rf"^{re.escape(q)}\.?$", re.I)).last.wait_for(timeout=timeout)


def wait_for_thinking_to_finish(page: Page, timeout: int = 180_000) -> None:
    thinking = page.get_by_text(re.compile(r"\bThinking\.\.\.|\bThinking\b", re.I))
    if thinking.count() > 0:
        try:
            thinking.first.wait_for(state="visible", timeout=5_000)
        except Exception:
            pass
        thinking.first.wait_for(state="hidden", timeout=timeout)
    page.wait_for_timeout(800)  # let response paint


def wait_for_user_query_echo(page: Page, query_text: str, timeout: int = 30_000) -> None:
    page.get_by_text(re.compile(rf"^{re.escape(query_text)}$", re.I)).last.wait_for(timeout=timeout)


def wait_for_agent_response_complete(page: Page, timeout: int = 180_000) -> None:
    page.get_by_text(
        re.compile(r"i've prepared|here are|i found|filter to list|results|output|query for", re.I)
    ).last.wait_for(timeout=timeout)


def wait_for_prompt(page: Page, prompt_text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
    """Wait for a specific prompt text to appear in the chat."""
    page.get_by_text(re.compile(rf"{re.escape(prompt_text)}", re.I)).wait_for(timeout=timeout)


def click_chip(page: Page, chip_text: str) -> None:
    """Click on a chip button by its text."""
    page.get_by_text(re.compile(re.escape(chip_text), re.I)).click(timeout=DEFAULT_TIMEOUT)

# -------- AIOps EC2 helpers --------

def open_suggestions_modal(page: Page) -> None:
    """Open the suggestions modal (assuming a button or icon triggers it)."""
    # Adjust selector based on UI; assuming a button with "suggestions" or similar
    page.get_by_role("button", name=re.compile(r"suggestions|browse", re.I)).click(timeout=DEFAULT_TIMEOUT)


def pick_from_modal_by_name_text(page: Page, name: str) -> None:
    """Pick an item from the modal by name text."""
    page.get_by_text(re.compile(re.escape(name), re.I)).click(timeout=DEFAULT_TIMEOUT)

#-------- Inventory Management helpers --------
def fill_instance_name_and_send(page: Page, name: str) -> None:
    """Fill the instance name and send."""
    # Assuming an input for name and a send button
    page.get_by_placeholder(re.compile(r"name", re.I)).fill(name)
    page.get_by_role("button", name=re.compile(r"send|submit", re.I)).click(timeout=DEFAULT_TIMEOUT)

#-------- Assertions --------
def assert_kms_and_success(page: Page) -> None:
    """Assert that KMS and success indicators are present."""
    # Assuming text or elements indicating success
    page.get_by_text(re.compile(r"kms|key management", re.I)).wait_for(timeout=DEFAULT_TIMEOUT)
    page.get_by_text(re.compile(r"success|completed", re.I)).wait_for(timeout=DEFAULT_TIMEOUT)

#-------- View Output helpers --------
def click_view_output_in_latest_message(page: Page, timeout: int = 180_000) -> None:
    deadline = time.time() + (timeout / 1000)

    while time.time() < deadline:
        buttons = page.get_by_role("button", name=re.compile(r"view output", re.I))
        if buttons.count() == 0:
            page.wait_for_timeout(500)
            continue

        view_btn = buttons.last

        try:
            expect(view_btn).to_be_visible(timeout=10_000)
            view_btn.scroll_into_view_if_needed(timeout=5_000)
            expect(view_btn).to_be_enabled(timeout=5_000)
            view_btn.click(timeout=10_000)
            page.wait_for_timeout(500)
            return
        except Exception:
            try:
                view_btn.click(timeout=10_000, force=True)
                page.wait_for_timeout(500)
                return
            except Exception:
                handle = view_btn.element_handle()
                if handle:
                    try:
                        page.evaluate("el => el.click()", handle)
                        page.wait_for_timeout(500)
                        return
                    except Exception:
                        pass
                page.wait_for_timeout(500)

    raise TimeoutError("View Output button never became clickable within timeout.")

#-------- OS Management helpers --------

def open_os_instance_picker(page: Page) -> None:
    picker = page.get_by_text(re.compile(r"click here to select an instance", re.I)).first
    expect(picker).to_be_visible(timeout=DEFAULT_TIMEOUT)
    picker.click(timeout=DEFAULT_TIMEOUT)


def wait_os_instances_or_empty(page: Page, timeout: int = 60_000) -> Tuple[object, int]:
    modal = page.locator("div[role='dialog']", has_text=re.compile(r"select an instance", re.I))
    modal.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)

    connect_btns = modal.get_by_role("button", name=re.compile(r"connect", re.I))

    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        if connect_btns.count() > 0:
            return modal, connect_btns.count()

        empty = modal.get_by_text(re.compile(r"no instances|no data|not found", re.I))
        if empty.count() > 0 and empty.first.is_visible():
            return modal, 0

        page.wait_for_timeout(500)

    return modal, connect_btns.count()


# -------- AIOps EC2 helpers --------

def click_chip(page: Page, label: str) -> None:
    page.get_by_role("button", name=label).click(timeout=DEFAULT_TIMEOUT)


def wait_for_prompt(page: Page, prompt_regex: str) -> None:
    page.get_by_text(re.compile(prompt_regex, re.I)).first.wait_for(timeout=DEFAULT_TIMEOUT)

# This function assumes the modal is already open and the options are loaded.
def open_suggestions_modal(page: Page) -> None:
    page.locator("button.bg-teal-600").first.click(timeout=DEFAULT_TIMEOUT)
    page.get_by_role("heading", name=re.compile(r"suggestions for resources", re.I)).wait_for(timeout=DEFAULT_TIMEOUT)

# This function assumes the modal is already open and the options are loaded.
def pick_from_modal_by_name_text(page: Page, name_text: str) -> None:
    row = page.locator("tr", has_text=name_text).first
    row.wait_for(timeout=DEFAULT_TIMEOUT)

    row.get_by_role("checkbox").first.click(timeout=DEFAULT_TIMEOUT)

    add_btn = page.get_by_role("button", name=re.compile(r"add to message", re.I))
    expect(add_btn).to_be_enabled(timeout=DEFAULT_TIMEOUT)
    add_btn.click(timeout=DEFAULT_TIMEOUT)

    page.wait_for_timeout(400)

# ------- Inventory Management helpers --------
def fill_instance_name_and_send(page: Page, instance_name: str) -> None:
    box = page.get_by_placeholder(re.compile(r"type next command", re.I))
    box.click(timeout=DEFAULT_TIMEOUT)
    box.fill(instance_name)

    send = page.get_by_role("button", name=re.compile(r"send", re.I))
    expect(send).to_be_enabled(timeout=DEFAULT_TIMEOUT)
    send.click(timeout=DEFAULT_TIMEOUT)

#-------- Assertions --------
def assert_kms_and_success(page: Page) -> None:
    expect(page.get_by_text(re.compile(r"alias\/MytestKMSkey|MytestKMSkey", re.I))).to_be_visible(timeout=90_000)
    expect(page.get_by_text(re.compile(r"EC2 instance was launched successfully", re.I))).to_be_visible(timeout=180_000)
    expect(page.locator("text=Something went wrong")).to_have_count(0)