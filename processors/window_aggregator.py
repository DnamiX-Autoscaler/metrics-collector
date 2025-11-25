# processors/window_aggregator.py

from collections import deque
from typing import Deque, Dict, Any, List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class SlidingWindowAggregator:
    """
    Simple sliding-window aggregator.

    Even though most aggregations are done by PromQL (rate(), histogram_quantile()),
    this can be used if you want to keep N recent rows per (namespace,service)
    and do additional temporal smoothing later.
    """

    def __init__(self, max_window_size: int = 10):
        # key: (namespace, service_name) -> deque[Dict]
        self.max_window_size = max_window_size
        self._windows: Dict[Tuple[str, str], Deque[Dict[str, Any]]] = {}

    def add_row(self, namespace: str, service_name: str, row: Dict[str, Any]) -> None:
        key = (namespace, service_name)
        if key not in self._windows:
            self._windows[key] = deque(maxlen=self.max_window_size)
        self._windows[key].append(row)
        logger.debug(
            "Added row to window %s/%s (size=%d)",
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
