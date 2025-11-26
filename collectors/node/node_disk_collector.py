# collectors/node/node_disk_collector.py

from typing import Dict
from utils.http_client import HTTPClient
from config.settings import PROMETHEUS_URL
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    data = client.get("/api/v1/query", params={"query": query})
    if data.get("status") != "success":
        logger.error("Disk query failed: %s", query)
        return {}

    out: Dict[str, float] = {}
    for item in data["data"]["result"]:
        instance = item["metric"].get("instance", "unknown-node")
        value = item.get("value", [None, "0"])[1]
        try:
            out[instance] = float(value)
        except Exception:
            out[instance] = 0.0

    return out


def collect_node_disk_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    # Reads per second (IOPS)
    read_query = (
        "sum by(instance)(irate(node_disk_reads_completed_total"
        f"[{window_size_seconds}s]))"
    )

    # Writes per second (IOPS)
    write_query = (
        "sum by(instance)(irate(node_disk_writes_completed_total"
        f"[{window_size_seconds}s]))"
    )

    read_map = _query_vector(read_query)
    write_map = _query_vector(write_query)

    combined: Dict[str, Dict[str, float]] = {}

    for node in set(read_map.keys()) | set(write_map.keys()):
        combined[node] = {
            "node_disk_read_iops": read_map.get(node, 0.0),
            "node_disk_write_iops": write_map.get(node, 0.0),
        }

    return combined
