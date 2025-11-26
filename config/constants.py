# config/constants.py

"""
Global constants used throughout the metrics collector.
Some can be overridden via environment variables.
"""

import os

# -------------------------------------------------------
# Sliding window + scrape interval (backup values)
# NOTE:
#   Main config still comes from config/settings.py
#   These are here only so older imports won't break.
# -------------------------------------------------------

WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))

# -------------------------------------------------------
# HTTP client retry behaviour (USED BY utils/http_client)
# -------------------------------------------------------

# Prometheus / HTTP call retry count
HTTP_RETRY_COUNT = int(os.getenv("HTTP_RETRY_COUNT", 3))

# Seconds to wait between retries
HTTP_RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", 1.0))

# -------------------------------------------------------
# Graph / centrality tuning
# -------------------------------------------------------

# Minimum RPS to keep an edge in the service graph
MIN_RPS_THRESHOLD = float(os.getenv("MIN_RPS_THRESHOLD", 0.01))

# Optional dataset version tag (if you want to track schema changes)
DATASET_VERSION = "v1.0"
