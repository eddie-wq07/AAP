"""Central configuration. All values read from environment / .env."""

import os
from dotenv import load_dotenv

load_dotenv()

HEADLESS: bool = os.getenv("HEADLESS", "true").lower() not in ("false", "0", "no")

SIMPLIFY_EMAIL: str = os.getenv("SIMPLIFY_EMAIL", "")
SIMPLIFY_PASSWORD: str = os.getenv("SIMPLIFY_PASSWORD", "")

NAV_TIMEOUT_MS: int = int(os.getenv("NAV_TIMEOUT_MS", "20000"))
