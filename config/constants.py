# config/constants.py

"""
Global constants used throughout the metrics collector.
These are intentionally separated from settings.py because
they are STATIC values, not environment-configurable.
"""

# -------------------------------------------------------
# Default sliding window + scrape interval
# -------------------------------------------------------

# Window used for rate(), irate(), histogram_quantile() etc.
WINDOW_SIZE_SECONDS = 30        # same as settings.py default

# Time to sleep between pipeline iterations
SCRAPE_INTERVAL_SECONDS = 30    # same as settings.py default

# -------------------------------------------------------
# Additional constants (if needed later)
# -------------------------------------------------------

# Minimum RPS required to include an edge in centrality graph
MIN_RPS_THRESHOLD = 0.01

# Placeholder for dataset column names prefix
DATASET_VERSION = "v1.0"

