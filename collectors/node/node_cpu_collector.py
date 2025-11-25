# collectors/node/node_cpu_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_node_cpu_usage(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Collect node CPU usage (%) per node (instance).
    Uses:
      node_cpu_seconds_total{mode="idle"}

    PromQL:
      100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[window])) * 100)

    Returns:
      {
        "instance-1": {"node_cpu_usage_percent": 43.2},
        "instance-2": {"node_cpu_usage_percent": 55.7},
        ...
      }
    """
    range_selector = f"[{window_size_seconds}s]"
    query = (
        f"100 - (avg by(instance)(irate("
        f"node_cpu_seconds_total{{mode=\"idle\"}}{range_selector}"
        f")) * 100)"
    )

    logger.info("Querying Prometheus for node CPU usage: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Prometheus CPU query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])
    cpu_map: Dict[str, Dict[str, float]] = {}

    for item in results:
        metric = item.get("metric", {})
        value = item.get("value", [None, "0"])[1]

        node_name = metric.get("instance", "unknown-node")
        try:
            cpu_percent = float(value)
        except (TypeError, ValueError):
            cpu_percent = 0.0

        cpu_map[node_name] = {
            "node_cpu_usage_percent": cpu_percent
        }

    return cpu_map
