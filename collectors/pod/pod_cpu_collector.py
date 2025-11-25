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
    Collect per-pod CPU usage using container_cpu_usage_seconds_total.

    PromQL:
      rate(container_cpu_usage_seconds_total{namespace="<ns>", pod!=""}[window])

    Converts CPU cores → CPU percentage:
      cpu_percent = cpu_core_usage * 100
    """
    range_selector = f"[{window_size_seconds}s]"

    query = (
        f"rate(container_cpu_usage_seconds_total{{namespace=\"{namespace}\", pod!=\"\", image!=\"\"}}"
        f"{range_selector})"
    )

    logger.info("Querying pod CPU: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Pod CPU query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])

    pod_map: Dict[str, List[float]] = {}

    for item in results:
        metric = item.get("metric", {})
        pod = metric.get("pod")
        if not pod:
            continue

        value = float(item.get("value", [None, "0"])[1])
        cpu_percent = value * 100  # CPU cores → %

        pod_map.setdefault(pod, []).append(cpu_percent)

    # Aggregate
    out: Dict[str, Dict[str, float]] = {}

    for pod, values in pod_map.items():
        out[pod] = {
            "pod_cpu_usage_percent_avg": safe_avg(values),
            "pod_cpu_usage_percent_p95": p95(values),
        }

    return out
