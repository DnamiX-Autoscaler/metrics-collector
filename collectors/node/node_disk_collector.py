# collectors/node/node_disk_collector.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict
from utils.http_client import HTTPClient
from config.settings import PROMETHEUS_URL
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    """
    Execute a PromQL query and return:
        { instance: value }
    """
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Disk query failed: %s", query)
        return {}

    out = {}
    for item in data["data"].get("result", []):
        instance = item["metric"].get("instance", "unknown")
        raw_val = item.get("value", [None, "0"])[1]
        try:
            out[instance] = float(raw_val)
        except:
            out[instance] = 0.0

    return out


def collect_node_disk_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Disk IO metrics (IOPS):
        - Read IOPS
        - Write IOPS
    """

    read_query = (
        "sum by(instance)("
        f"irate(node_disk_reads_completed_total[{window_size_seconds}s])"
        ")"
    )

    write_query = (
        "sum by(instance)("
        f"irate(node_disk_writes_completed_total[{window_size_seconds}s])"
        ")"
    )

    read_map = _query_vector(read_query)
    write_map = _query_vector(write_query)

    combined = {}

    for instance in set(read_map.keys()) | set(write_map.keys()):
        combined[instance] = {
            "node_disk_read_iops": read_map.get(instance, 0.0),
            "node_disk_write_iops": write_map.get(instance, 0.0),
        }

    logger.info("Node disk metrics collected: %s", combined)
    return combined
