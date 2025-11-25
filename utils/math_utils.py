# utils/math_utils.py
import numpy as np
from typing import List


def p95(values: List[float]) -> float:
    """Return 95th percentile."""
    if not values:
        return 0.0
    return float(np.percentile(values, 95))


def p99(values: List[float]) -> float:
    """Return 99th percentile."""
    if not values:
        return 0.0
    return float(np.percentile(values, 99))


def safe_avg(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def rate(delta_value: float, seconds: float) -> float:
    """Simple rate = Δvalue / time."""
    if seconds <= 0:
        return 0.0
    return delta_value / seconds
