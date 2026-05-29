"""Playwright form filler: navigate to a Simplify apply URL and submit.

Handles the most common Simplify-hosted application form fields.
Run standalone for quick testing:
    python applicator/form_filler.py <apply_url>
"""

import os
import random
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

load_dotenv()

SUBMIT_SELECTORS = [
    'button[type="submit"]:has-text("Submit")',
    'button:has-text("Submit Application")',
    'button:has-text("Apply")',
    'button[type="submit"]',
]

# Map of common label text → env var to pull the value from.
FIELD_MAP: dict[str, str] = {
    "first name": "APPLICANT_FIRST_NAME",
    "last name": "APPLICANT_LAST_NAME",
    "email": "SIMPLIFY_EMAIL",
    "phone": "APPLICANT_PHONE",
    "linkedin": "APPLICANT_LINKEDIN",
    "github": "APPLICANT_GITHUB",
    "website": "APPLICANT_WEBSITE",
    "city": "APPLICANT_CITY",
    "state": "APPLICANT_STATE",
    "zip": "APPLICANT_ZIP",
    "country": "APPLICANT_COUNTRY",
}


def _random_delay(min_s: float = 0.5, max_s: float = 1.5) -> None:
    time.sleep(random.uniform(min_s, max_s))


def _fill_text_fields(page: Page) -> None:
    inputs = page.locator("input[type='text'], input[type='email'], input[type='tel'], input:not([type])")
    count = inputs.count()
    for i in range(count):
        field = inputs.nth(i)
        # Try to identify via placeholder or aria-label
        placeholder = (field.get_attribute("placeholder") or "").lower()
        aria_label = (field.get_attribute("aria-label") or "").lower()
        label_text = placeholder or aria_label

        for keyword, env_var in FIELD_MAP.items():
            if keyword in label_text:
                value = os.getenv(env_var, "")
                if value:
                    field.fill(value)
                    _random_delay(0.2, 0.5)
                break


def _upload_resume(page: Page) -> None:
    resume_path = os.getenv("RESUME_PATH", "")
    if not resume_path or not os.path.isfile(resume_path):
        return
    upload = page.locator('input[type="file"]').first
    if upload.count() > 0:
        upload.set_input_files(resume_path)
        _random_delay()


def _click_submit(page: Page) -> bool:
    for selector in SUBMIT_SELECTORS:
        btn = page.locator(selector).first
        if btn.count() > 0 and btn.is_enabled():
            btn.click()
            return True
    return False


def fill_and_submit(page: Page, apply_url: str) -> bool:
    """Navigate to apply_url, fill the form, submit. Returns True on success."""
    page.goto(apply_url, wait_until="domcontentloaded", timeout=config.NAV_TIMEOUT_MS)
    _random_delay()

    _fill_text_fields(page)
    _upload_resume(page)
    _random_delay()

    submitted = _click_submit(page)
    if submitted:
        # Wait briefly for confirmation page / URL change
        try:
            page.wait_for_load_state("networkidle", timeout=5_000)
        except Exception:
            pass
    return submitted


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python applicator/form_filler.py <apply_url>", file=sys.stderr)
        sys.exit(1)

    apply_url = sys.argv[1]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.HEADLESS)
        try:
            page = browser.new_context().new_page()
            success = fill_and_submit(page, apply_url)
            if success:
                print(f"Submitted application at: {apply_url}")
            else:
                print(f"WARNING: could not find submit button at: {apply_url}", file=sys.stderr)
                sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
