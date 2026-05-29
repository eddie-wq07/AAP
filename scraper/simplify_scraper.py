"""Simplify.jobs scraper: log in, grab the first job, print it.

Run from the repo root: `python scraper/simplify_scraper.py`.
Reads SIMPLIFY_EMAIL / SIMPLIFY_PASSWORD from .env and HEADLESS from config.py.
"""

import os
import random
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

load_dotenv()

LOGIN_URL = "https://simplify.jobs/auth/login"
JOBS_URL = "https://simplify.jobs/jobs"
DESC_SNIPPET_CHARS = 500
NAV_TIMEOUT_MS = 20_000

TITLE_SELECTORS = ['[data-testid="job-title"]', "h1"]
COMPANY_SELECTORS = ['[data-testid="company-name"]', 'a[href*="/company"]', "h2"]
DESCRIPTION_SELECTORS = [
    '[data-testid="job-description"]',
    'section:has(h3:has-text("Description"))',
    "article",
]
APPLY_SELECTORS = [
    '[data-testid="apply-button"]',
    'a:has-text("Apply")',
    'a[href*="apply"]',
]
JOB_CARD_SELECTORS = [
    '[data-testid="job-card"]',
    'article a[href*="/jobs/"]',
    'a[href*="/job/"]',
]


def random_delay(min_s: float = 1.0, max_s: float = 2.0) -> None:
    time.sleep(random.uniform(min_s, max_s))


def login(page, email: str, password: str) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
    page.fill('input[type="email"], input[name="email"]', email)
    page.fill('input[type="password"], input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(
        lambda url: "/auth/login" not in url, timeout=NAV_TIMEOUT_MS
    )


def _first_text(page, selectors: list[str]) -> str:
    for selector in selectors:
        locator = page.locator(selector).first
        if locator.count() == 0:
            continue
        text = (locator.inner_text() or "").strip()
        if text:
            return text
    raise LookupError(f"none of {selectors} matched a non-empty element")


def _apply_url(page) -> str:
    for selector in APPLY_SELECTORS:
        locator = page.locator(selector).first
        if locator.count() == 0:
            continue
        href = (locator.get_attribute("href") or "").strip()
        if not href:
            continue
        return href if href.startswith("http") else locator.evaluate("el => el.href")
    raise LookupError(f"none of {APPLY_SELECTORS} resolved to an apply link")


def extract_first_job(page) -> dict:
    page.goto(JOBS_URL, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
    card_selector = ", ".join(JOB_CARD_SELECTORS)
    page.wait_for_selector(card_selector, timeout=NAV_TIMEOUT_MS)
    page.locator(card_selector).first.click()
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
    return {
        "title": _first_text(page, TITLE_SELECTORS),
        "company": _first_text(page, COMPANY_SELECTORS),
        "description": _first_text(page, DESCRIPTION_SELECTORS),
        "apply_url": _apply_url(page),
    }


def print_job(job: dict) -> None:
    desc = job["description"]
    snippet = desc[:DESC_SNIPPET_CHARS] + (
        "..." if len(desc) > DESC_SNIPPET_CHARS else ""
    )
    print(f"Title:       {job['title']}")
    print(f"Company:     {job['company']}")
    print(f"Apply URL:   {job['apply_url']}")
    print(f"Description: {snippet}")


def main() -> None:
    email = os.environ.get("SIMPLIFY_EMAIL")
    password = os.environ.get("SIMPLIFY_PASSWORD")
    if not email or not password:
        print(
            "ERROR: SIMPLIFY_EMAIL and SIMPLIFY_PASSWORD must be set in .env",
            file=sys.stderr,
        )
        sys.exit(1)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.HEADLESS)
        try:
            page = browser.new_context().new_page()
            try:
                login(page, email, password)
            except Exception as e:
                raise RuntimeError(f"Login to simplify.jobs failed: {e}") from e
            random_delay()
            try:
                job = extract_first_job(page)
            except Exception as e:
                raise RuntimeError(f"Job extraction failed: {e}") from e
            print_job(job)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
