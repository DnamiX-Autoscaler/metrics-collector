# collectors/pod/pod_memory_collector.py

from typing import Dict, List
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.math_utils import p95, safe_avg
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

def collect_pod_memory_usage(namespace: str) -> Dict[str, Dict[str, float]]:
    """
    Docker Desktop FIX:
    container_memory_usage_bytes also has NO namespace label.
    """

    query = 'container_memory_usage_bytes{pod!=""}'

    logger.info("Querying POD Memory (docker-desktop fix): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Pod Memory query failed: %s", data)
        return {}

    results = data["data"].get("result", [])
    mem_map: Dict[str, List[float]] = {}

    for item in results:
        metric = item.get("metric", {})
        pod = metric.get("pod")
        if not pod:
            continue

        try:
            bytes_val = float(item["value"][1])
        except:
            bytes_val = 0.0

        mem_mb = bytes_val / (1024 * 1024)
        mem_map.setdefault(pod, []).append(mem_mb)

    out = {}
    for pod, values in mem_map.items():
        out[pod] = {
            "pod_memory_usage_mb_avg": safe_avg(values),
            "pod_memory_usage_mb_p95": p95(values),
        }

    return out
