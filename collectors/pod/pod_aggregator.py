# collectors/pod/pod_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from collectors.pod.pod_cpu_collector import collect_pod_cpu_usage
from collectors.pod.pod_memory_collector import collect_pod_memory_usage
from collectors.pod.pod_restart_collector import collect_pod_restart_count
from collectors.pod.pod_limits_collector import collect_pod_limits

logger = get_logger(__name__)

MetricMap = Dict[str, Dict[str, Any]]


def collect_pod_metrics(namespace: str, window_size_seconds: int) -> MetricMap:
    """
    Aggregates all pod metrics into a single dict per pod.

    Returns:
      {
        "pod-1": {
          pod_cpu_usage_percent_avg: ...,
          pod_cpu_usage_percent_p95: ...,
          pod_memory_usage_mb_avg: ...,
          pod_memory_usage_mb_p95: ...,
          pod_restart_count: ...,
          pod_cpu_limit_percent: ...,
          pod_memory_limit_percent: ...
        },
        ...
      }
    """

    logger.info("Collecting POD metrics for namespace=%s", namespace)

    cpu_map = collect_pod_cpu_usage(namespace, window_size_seconds)
    mem_map = collect_pod_memory_usage(namespace)
    rst_map = collect_pod_restart_count(namespace)
    lim_map = collect_pod_limits(namespace)

    merged: MetricMap = {}

    all_pods = (
        set(cpu_map.keys())
        | set(mem_map.keys())
        | set(rst_map.keys())
        | set(lim_map.keys())
    )

    for pod in all_pods:
        merged[pod] = {}
        if pod in cpu_map:
            merged[pod].update(cpu_map[pod])
        if pod in mem_map:
            merged[pod].update(mem_map[pod])
        if pod in rst_map:
            merged[pod].update(rst_map[pod])
        if pod in lim_map:
            merged[pod].update(lim_map[pod])

    # Add pod count for namespace
    for pod in merged:
        merged[pod]["current_pod_count"] = len(all_pods)

    return merged
