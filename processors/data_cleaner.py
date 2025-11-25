# processors/data_cleaner.py

from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


def _to_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    """Safely convert to int."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clean_numeric_fields(row: Dict[str, Any], numeric_fields: List[str]) -> Dict[str, Any]:
    """
    Normalize numeric fields:
      - convert to float
      - replace invalid with 0.0
    """

    cleaned = dict(row)

    for field in numeric_fields:
        if field not in cleaned:
            cleaned[field] = 0.0
        else:
            cleaned[field] = _to_float(cleaned[field], 0.0)

    return cleaned


def clamp_percentages(row: Dict[str, Any], percent_fields: List[str]) -> Dict[str, Any]:
    """
    Clamp percentage fields to [0, 100].
    """

    for field in percent_fields:
        val = _to_float(row.get(field, 0.0), 0.0)
        if val < 0:
            val = 0.0
        if val > 100:
            val = 100.0
        row[field] = val

    return row


def ensure_non_negative(row: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Replace negative values with 0 for given fields.
    """

    for field in fields:
        val = _to_float(row.get(field, 0.0), 0.0)
        if val < 0:
            val = 0.0
        row[field] = val

    return row
