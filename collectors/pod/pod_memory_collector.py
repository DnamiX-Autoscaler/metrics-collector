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
    Collect pod-level memory usage (RSS).

    PromQL:
      container_memory_usage_bytes{namespace="<ns>", pod!=""}
    """
    query = (
        f"container_memory_usage_bytes{{namespace=\"{namespace}\", pod!=\"\", image!=\"\"}}"
    )

    logger.info("Querying pod memory: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Pod Memory query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])

    mem_map: Dict[str, List[float]] = {}

    for item in results:
        metric = item.get("metric", {})
        pod = metric.get("pod")
        if not pod:
            continue

        value = float(item.get("value", [None, "0"])[1])
        mem_mb = value / (1024 * 1024)

        mem_map.setdefault(pod, []).append(mem_mb)

    # Aggregate
    out: Dict[str, Dict[str, float]] = {}

    for pod, values in mem_map.items():
        out[pod] = {
            "pod_memory_usage_mb_avg": safe_avg(values),
            "pod_memory_usage_mb_p95": p95(values),
        }

    return out
