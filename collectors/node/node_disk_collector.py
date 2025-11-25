# collectors/node/node_disk_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    logger.info("Querying Prometheus (disk): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Prometheus disk query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])
    out: Dict[str, float] = {}

    for item in results:
        metric = item.get("metric", {})
        value = item.get("value", [None, "0"])[1]
        node_name = metric.get("instance", "unknown-node")
        try:
            val = float(value)
        except (TypeError, ValueError):
            val = 0.0

        out[node_name] = val

    return out


def collect_node_disk_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Collect node-level disk read/write IOPS.

    PromQL:

      node_disk_read_iops =
        sum by(instance)(
          irate(node_disk_reads_completed_total[window])
        )

      node_disk_write_iops =
        sum by(instance)(
          irate(node_disk_writes_completed_total[window])
        )
    """
    range_selector = f"[{window_size_seconds}s]"

    query_read = (
        "sum by(instance)("
        f"irate(node_disk_reads_completed_total{range_selector})"
        ")"
    )

    query_write = (
        "sum by(instance)("
        f"irate(node_disk_writes_completed_total{range_selector})"
        ")"
    )

    read_map = _query_vector(query_read)
    write_map = _query_vector(query_write)

    combined: Dict[str, Dict[str, float]] = {}
    all_nodes = set(read_map.keys()) | set(write_map.keys())

    for node in all_nodes:
        combined[node] = {
            "node_disk_read_iops": read_map.get(node, 0.0),
            "node_disk_write_iops": write_map.get(node, 0.0),
        }

    return combined
