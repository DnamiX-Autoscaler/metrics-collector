# collectors/node/node_memory_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    """Helper: run PromQL and return {instance: value} map."""
    logger.info("Querying Prometheus (memory): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Prometheus memory query failed: %s", data)
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


def collect_node_memory_usage() -> Dict[str, Dict[str, float]]:
    """
    Collect node memory usage:
      - node_memory_usage_percent
      - node_memory_usage_mb

    PromQL:

      usage_percent =
        ((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
          / node_memory_MemTotal_bytes) * 100

      usage_mb =
        (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
        / (1024 * 1024)

    Returns:
      {
        "instance-1": {
          "node_memory_usage_percent": ...,
          "node_memory_usage_mb": ...
        },
        ...
      }
    """

    # Percent
    query_percent = (
        "((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        "/ node_memory_MemTotal_bytes) * 100"
    )

    # MB usage
    query_mb = (
        "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        "/ (1024 * 1024)"
    )

    percent_map = _query_vector(query_percent)
    mb_map = _query_vector(query_mb)

    combined: Dict[str, Dict[str, float]] = {}

    # union of all node names
    all_nodes = set(percent_map.keys()) | set(mb_map.keys())

    for node in all_nodes:
        combined[node] = {
            "node_memory_usage_percent": percent_map.get(node, 0.0),
            "node_memory_usage_mb": mb_map.get(node, 0.0),
        }

    return combined
