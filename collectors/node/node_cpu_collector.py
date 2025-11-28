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
    Collect CPU Usage (%) per node using cAdvisor metrics.

    Caps values into 0–100 range because cAdvisor can report >100%
    if summed across containers or cores.
    """

    query = (
        f"sum by (instance) (rate(container_cpu_usage_seconds_total[{window_size_seconds}s])) * 100"
    )

    logger.info("Querying node CPU usage: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("CPU query failed: %s", data.get("error", "Unknown error"))
        return {}

    results = data["data"].get("result", [])
    logger.info("CPU query returned %d results", len(results))

    cpu_map = {}

    for item in results:
        instance = item["metric"].get("instance", "unknown-node")
        raw_val = item.get("value", [None, "0"])[1]

        # Convert to float
        try:
            cpu_percent = float(raw_val)
        except ValueError:
            cpu_percent = 0.0

        # Fix negative values
        if cpu_percent < 0:
            cpu_percent = 0.0

        # 100% HARD CAP
        if cpu_percent > 100:
            logger.warning(
                "CPU usage %.3f%% for %s exceeded 100%% — capped.",
                cpu_percent,
                instance,
            )
            cpu_percent = 100.0

        cpu_map[instance] = {
            "node_cpu_usage_percent": round(cpu_percent, 3)
        }

    logger.info("Final CPU map: %s", cpu_map)
    return cpu_map

