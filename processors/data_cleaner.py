# processors/data_cleaner.py

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert safely to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    """Convert safely to int."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clean_numeric_fields(
    row: Dict[str, Any], numeric_fields: List[str]
) -> Dict[str, Any]:
    """
    Normalize numeric fields:
      - convert to float
      - replace errors with 0.0
    """

    cleaned = dict(row)

    for field in numeric_fields:
        cleaned[field] = _to_float(cleaned.get(field, 0.0), 0.0)

    return cleaned


def clamp_percentages(row: Dict[str, Any], percent_fields: List[str]) -> Dict[str, Any]:
    """Clamp percentage fields into valid range [0,100]."""

    for field in percent_fields:
        value = _to_float(row.get(field, 0.0), 0.0)
        if value < 0:
            value = 0.0
        if value > 100:
            value = 100.0
        row[field] = value

    return row


def ensure_non_negative(row: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Ensure that fields do not contain negative values."""

    for field in fields:
        value = _to_float(row.get(field, 0.0), 0.0)
        if value < 0:
            value = 0.0
        row[field] = value

    return row
