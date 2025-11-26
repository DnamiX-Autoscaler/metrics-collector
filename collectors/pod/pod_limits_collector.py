# collectors/pod/pod_limits_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_pod_limits(namespace: str) -> Dict[str, Dict[str, float]]:
    """
    Collect CPU + Memory resource limits per pod.

    Metric source:
      kube_pod_container_resource_limits

    PromQL:
      CPU:
        kube_pod_container_resource_limits{
          resource="cpu", namespace="<ns>"
        }

      Memory:
        kube_pod_container_resource_limits{
          resource="memory", namespace="<ns>"
        }

    We convert:
      cpu_limit_cores -> pod_cpu_limit_percent (cores * 100)
      memory_limit_bytes -> pod_memory_limit_percent (MB, name kept for schema)
    """

    query_cpu = (
        "kube_pod_container_resource_limits"
        f'{{resource="cpu", namespace="{namespace}"}}'
    )
    query_mem = (
        "kube_pod_container_resource_limits"
        f'{{resource="memory", namespace="{namespace}"}}'
    )

    logger.info("Querying pod resource limits (CPU + Memory) for ns=%s", namespace)

    cpu_data = client.get("/api/v1/query", params={"query": query_cpu})
    mem_data = client.get("/api/v1/query", params={"query": query_mem})

    out: Dict[str, Dict[str, float]] = {}

    # CPU limits
    if cpu_data.get("status") == "success":
        for item in cpu_data.get("data", {}).get("result", []):
            metric = item.get("metric", {})
            pod = metric.get("pod")
            if not pod:
                continue

            raw_val = item.get("value", [None, "0"])[1]
            try:
                cores = float(raw_val)
            except (TypeError, ValueError):
                cores = 0.0

            out.setdefault(pod, {})["cpu_limit_cores"] = cores

    # Memory limits
    if mem_data.get("status") == "success":
        for item in mem_data.get("data", {}).get("result", []):
            metric = item.get("metric", {})
            pod = metric.get("pod")
            if not pod:
                continue

            raw_val = item.get("value", [None, "0"])[1]
            try:
                bytes_val = float(raw_val)
            except (TypeError, ValueError):
                bytes_val = 0.0

            out.setdefault(pod, {})["memory_limit_bytes"] = bytes_val

    # Convert to "percent-like" fields used in your final dataset
    for pod, d in out.items():
        cpu_limit_cores = d.get("cpu_limit_cores", 0.0)
        mem_limit_bytes = d.get("memory_limit_bytes", 0.0)

        # 1 core = 100% (for scaling logic)
        cpu_limit_percent = cpu_limit_cores * 100.0

        # Memory "percent" you defined is actually MB in your dataset schema
        mem_limit_mb = mem_limit_bytes / (1024 * 1024)

        d["pod_cpu_limit_percent"] = cpu_limit_percent
        d["pod_memory_limit_percent"] = mem_limit_mb

    return out
