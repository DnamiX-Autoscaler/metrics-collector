# utils/http_client.py
import requests
from typing import Any, Dict
from config.constants import HTTP_RETRY_COUNT, HTTP_RETRY_DELAY
from utils.logger import get_logger
import time

logger = get_logger(__name__)


class HTTPClient:
    """Simple wrapper around requests with retry logic."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        for attempt in range(1, HTTP_RETRY_COUNT + 1):
            try:
                r = requests.get(url, params=params, timeout=5)
                r.raise_for_status()
                return r.json()

            except Exception as e:
                logger.error(f"HTTP GET failed {attempt}/{HTTP_RETRY_COUNT}: {e}")
                time.sleep(HTTP_RETRY_DELAY)

        raise RuntimeError(f"Failed GET after {HTTP_RETRY_COUNT} retries: {url}")
