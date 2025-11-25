# utils/time_utils.py
import time
from datetime import datetime, timezone


def now_utc() -> float:
    """Return current UTC timestamp (float seconds)."""
    return time.time()


def floor_to_window_start(ts: float, window_size: int) -> float:
    """Floor timestamp to nearest window boundary."""
    return ts - (ts % window_size)


def utc_ts_to_iso(ts: float) -> str:
    """Timestamp → ISO 8601 UTC format."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
