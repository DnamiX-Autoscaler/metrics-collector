# collectors/pod/pod_limits_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_pod_limits(namespace: str) -> Dict[str, Dict[str, float]]:
    """
    Collect CPU + Memory resource limits.

    CPU PromQL:
      kube_pod_container_resource_limits{resource="cpu", namespace="<ns>"}

    Memory PromQL:
      kube_pod_container_resource_limits{resource="memory", namespace="<ns>"}
    """

    query_cpu = (
        f"kube_pod_container_resource_limits{{resource=\"cpu\", namespace=\"{namespace}\"}}"
    )
    query_mem = (
        f"kube_pod_container_resource_limits{{resource=\"memory\", namespace=\"{namespace}\"}}"
    )

    logger.info("Querying pod resource limits...")

    cpu_data = client.get("/api/v1/query", params={"query": query_cpu})
    mem_data = client.get("/api/v1/query", params={"query": query_mem})

    out: Dict[str, Dict[str, float]] = {}

    # Parse CPU limits (in cores)
    for item in cpu_data.get("data", {}).get("result", []):
        pod = item.get("metric", {}).get("pod")
        if not pod:
            continue
        val = float(item.get("value", [None, "0"])[1])
        out.setdefault(pod, {})["cpu_limit_cores"] = val

    # Parse Memory limits (in bytes)
    for item in mem_data.get("data", {}).get("result", []):
        pod = item.get("metric", {}).get("pod")
        if not pod:
            continue
        val = float(item.get("value", [None, "0"])[1])
        out.setdefault(pod, {})["memory_limit_bytes"] = val

    # Convert to %
    for pod, d in out.items():
        cpu_limit = d.get("cpu_limit_cores", 0)
        mem_limit_bytes = d.get("memory_limit_bytes", 0)

        # Convert to percentages (compared to 1 full core)
        cpu_limit_percent = cpu_limit * 100

        mem_limit_percent = (mem_limit_bytes / (1024 * 1024))  # MB

        d["pod_cpu_limit_percent"] = cpu_limit_percent
        d["pod_memory_limit_percent"] = mem_limit_percent

    return out
