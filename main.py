"""Phase 1 orchestrator: scrape one job from Simplify, fill and submit the application.

Run: python main.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import config
from scraper.simplify_scraper import login, extract_first_job
from applicator.form_filler import fill_and_submit

load_dotenv()

APPLIED_LOG = Path("data/applied_jobs.json")


def _load_log() -> list[dict]:
    if APPLIED_LOG.exists():
        with open(APPLIED_LOG) as f:
            return json.load(f)
    return []


def _save_log(entries: list[dict]) -> None:
    APPLIED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(APPLIED_LOG, "w") as f:
        json.dump(entries, f, indent=2)


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

            print("Logging in to Simplify.jobs...")
            try:
                login(page, email, password)
            except Exception as e:
                print(f"ERROR: Login failed: {e}", file=sys.stderr)
                sys.exit(1)

            print("Finding first job...")
            try:
                job = extract_first_job(page)
            except Exception as e:
                print(f"ERROR: Could not extract job: {e}", file=sys.stderr)
                sys.exit(1)

            print(f"  Title:   {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  URL:     {job['apply_url']}")

            print("Filling and submitting application...")
            success = fill_and_submit(page, job["apply_url"])

            log = _load_log()
            entry = {
                **job,
                "applied_at": datetime.now(timezone.utc).isoformat(),
                "status": "submitted" if success else "form_not_found",
            }
            log.append(entry)
            _save_log(log)

            if success:
                print(f"\nDone. Applied to {job['title']} at {job['company']}.")
            else:
                print(
                    f"\nWARNING: Navigated to application but could not locate submit button.",
                    file=sys.stderr,
                )
                sys.exit(1)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
