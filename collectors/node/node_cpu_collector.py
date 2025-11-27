# collectors/node/node_cpu_collector.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_node_cpu_usage(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    CPU Usage % using cAdvisor metrics.
    """

    query = (
        f"sum by (instance) (rate(container_cpu_usage_seconds_total[{window_size_seconds}s])) * 100"
    )

    logger.info("Querying node CPU usage: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("CPU query failed: %s", data.get("error", "Unknown error"))
        return {}

    cpu_map = {}

    for item in data["data"].get("result", []):
        instance = item["metric"].get("instance", "unknown-node")
        raw_val = item.get("value", [None, "0"])[1]

        try:
            cpu = float(raw_val)
        except:
            cpu = 0.0

        if cpu < 0: cpu = 0.0
        if cpu > 100: cpu = 100.0

        cpu_map[instance] = {"node_cpu_usage_percent": round(cpu, 3)}

    return cpu_map
