# collectors/pod/pod_cpu_collector.py

from typing import Dict, List
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.math_utils import p95, safe_avg
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

def collect_pod_cpu_usage(namespace: str, window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Docker Desktop FIX:
    container_cpu_usage_seconds_total does NOT have namespace label.
    So filter only by pod!="".
    """

    query = (
        "rate(container_cpu_usage_seconds_total"
        f'{{pod!="", id!=""}}[{window_size_seconds}s])'
    )

    logger.info("Querying POD CPU (docker-desktop fix): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Pod CPU query failed: %s", data)
        return {}

    results = data["data"].get("result", [])
    cpu_map: Dict[str, List[float]] = {}

    for item in results:
        metric = item.get("metric", {})
        pod = metric.get("pod")
        if not pod:
            continue

        raw_val = item["value"][1]
        try:
            cores = float(raw_val)
        except:
            cores = 0.0

        cpu_percent = cores * 100.0
        cpu_map.setdefault(pod, []).append(cpu_percent)

    out = {}
    for pod, values in cpu_map.items():
        out[pod] = {
            "pod_cpu_usage_percent_avg": safe_avg(values),
            "pod_cpu_usage_percent_p95": p95(values),
        }

    return out
