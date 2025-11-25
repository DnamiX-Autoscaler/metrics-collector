# config/constants.py

# Time window boundaries
DEFAULT_WINDOW_SECONDS = 30
DEFAULT_QUERY_STEP = "15s"

# Retry logic for Prometheus HTTP
HTTP_RETRY_COUNT = 3
HTTP_RETRY_DELAY = 1  # seconds

# For network traffic → bytes to kilobytes
BYTES_TO_KB = 1 / 1024
BYTES_TO_MB = 1 / (1024 * 1024)
