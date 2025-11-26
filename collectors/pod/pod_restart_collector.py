# collectors/pod/pod_restart_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_pod_restart_count(namespace: str) -> Dict[str, Dict[str, float]]:
    """
    Collect pod restart counts (per pod).

    Metric source:
      kube_pod_container_status_restarts_total

    PromQL:
      kube_pod_container_status_restarts_total{namespace="<ns>"}
    """
    query = (
        "kube_pod_container_status_restarts_total"
        f'{{namespace="{namespace}"}}'
    )

    logger.info("Querying pod restart count: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Restart count query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])
    out: Dict[str, Dict[str, float]] = {}

    for item in results:
        metric = item.get("metric", {})
        pod = metric.get("pod")
        if not pod:
            continue

        raw_val = item.get("value", [None, "0"])[1]
        try:
            count = float(raw_val)
        except (TypeError, ValueError):
            count = 0.0

        out[pod] = {"pod_restart_count": count}

    return out
