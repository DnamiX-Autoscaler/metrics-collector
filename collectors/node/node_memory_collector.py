# collectors/node/node_memory_collector.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_value(query: str) -> float:
    data = client.get("/api/v1/query", params={"query": query})
    if data.get("status") != "success":
        return 0.0

    results = data["data"].get("result", [])
    if not results:
        return 0.0

    try:
        return float(results[0]["value"][1])
    except:
        return 0.0


def collect_node_memory_usage() -> Dict[str, Dict[str, float]]:
    percent_query = (
        "( (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        " / node_memory_MemTotal_bytes ) * 100"
    )

    mb_query = (
        "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) "
        " / 1024 / 1024"
    )

    usage_percent = round(_query_value(percent_query), 3)
    usage_mb = round(_query_value(mb_query), 3)

    # return raw — aggregator will assign node name
    return {
        "auto": {
            "node_memory_usage_percent": usage_percent,
            "node_memory_usage_mb": usage_mb,
        }
    }
