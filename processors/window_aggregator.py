# processors/window_aggregator.py

from collections import deque
from typing import Deque, Dict, Any, List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class SlidingWindowAggregator:
    """Maintain N latest dataset rows for smoothing/window ops."""

    def __init__(self, max_window_size: int = 10):
        self.max_window_size = max_window_size
        self._windows: Dict[Tuple[str, str], Deque[Dict[str, Any]]] = {}

    def add_row(self, namespace: str, service_name: str, row: Dict[str, Any]) -> None:
        key = (namespace, service_name)
        if key not in self._windows:
            self._windows[key] = deque(maxlen=self.max_window_size)
        self._windows[key].append(row)

        logger.debug(
            "Added window row %s/%s (size=%d)",
            namespace,
            service_name,
            len(self._windows[key]),
        )

    def get_window(self, namespace: str, service_name: str) -> List[Dict[str, Any]]:
        key = (namespace, service_name)
        return list(self._windows.get(key, deque()))

    def clear(self, namespace: str, service_name: str) -> None:
        key = (namespace, service_name)
        if key in self._windows:
            del self._windows[key]
