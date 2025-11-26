# collectors/node/node_cpu_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_node_cpu_usage(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    CPU Usage (%) per node.

    PromQL:
    100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[window])) * 100)
    """

    query = (
        "100 - (avg by(instance)("
        f"irate(node_cpu_seconds_total{{mode=\"idle\"}}[{window_size_seconds}s])"
        ") * 100)"
    )

    logger.info("Querying node CPU usage: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Node CPU query failed")
        return {}

    results = data["data"]["result"]
    cpu_map = {}

    for item in results:
        instance = item["metric"].get("instance", "unknown-node")
        value = item.get("value", [None, "0"])[1]

        try:
            cpu = float(value)
        except:
            cpu = 0.0

        cpu_map[instance] = {"node_cpu_usage_percent": cpu}

    return cpu_map
