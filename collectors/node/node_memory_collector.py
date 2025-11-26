# collectors/node/node_memory_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    data = client.get("/api/v1/query", params={"query": query})
    if data.get("status") != "success":
        logger.error("Node memory query failed: %s", query)
        return {}

    out = {}
    for item in data["data"]["result"]:
        instance = item["metric"].get("instance", "unknown-node")
        value = item.get("value", [None, "0"])[1]

        try:
            out[instance] = float(value)
        except:
            out[instance] = 0.0

    return out


def collect_node_memory_usage() -> Dict[str, Dict[str, float]]:
    """
    Memory usage % and MB.
    """

    percent_query = (
        "( (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        " / node_memory_MemTotal_bytes ) * 100"
    )

    mb_query = (
        "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        "/ 1024 / 1024"
    )

    percent_map = _query_vector(percent_query)
    mb_map = _query_vector(mb_query)

    combined = {}

    for node in set(percent_map.keys()) | set(mb_map.keys()):
        combined[node] = {
            "node_memory_usage_percent": percent_map.get(node, 0.0),
            "node_memory_usage_mb": mb_map.get(node, 0.0),
        }

    return combined
