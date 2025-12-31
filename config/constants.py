# config/constants.py

"""
Global constants.
⚠️ These MUST be environment-driven or derived.
NO service names / namespaces here.
"""

import os

# -------------------------------------------------------
# Dataset / schema
# -------------------------------------------------------
DATASET_VERSION = os.getenv("DATASET_VERSION", "v1.0")

# -------------------------------------------------------
# Sliding window & scrape timing (fallbacks only)
# -------------------------------------------------------
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))

# -------------------------------------------------------
# HTTP client retry behavior (used by utils/http_client)
# -------------------------------------------------------
HTTP_RETRY_COUNT = int(os.getenv("HTTP_RETRY_COUNT", 3))
HTTP_RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", 1.0))

# -------------------------------------------------------
# Graph / centrality tuning
# -------------------------------------------------------
MIN_RPS_THRESHOLD = float(os.getenv("MIN_RPS_THRESHOLD", 0.01))
