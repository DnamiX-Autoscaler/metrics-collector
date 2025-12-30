from typing import Dict, Any, List
from utils.math_utils import safe_avg, p95


def aggregate_pods_for_service(
    pod_map: Dict[str, Dict[str, Any]],
    service_name: str,
) -> Dict[str, float]:
    """
    Aggregate pod-level metrics for all pods belonging to a service.

    pod names example:
      order-service-778d9645c5-9zbxk
    service_name:
      order-service
    """

    matched_pods = [
        metrics
        for pod_name, metrics in pod_map.items()
        if pod_name.startswith(service_name)
    ]

    if not matched_pods:
        return {
            "current_pod_count": 0,
            "pod_cpu_usage_percent_avg": 0.0,
            "pod_cpu_usage_percent_p95": 0.0,
            "pod_memory_usage_mb_avg": 0.0,
            "pod_memory_usage_mb_p95": 0.0,
            "pod_restart_count": 0.0,
            "pod_cpu_limit_percent": 0.0,
            "pod_memory_limit_percent": 0.0,
        }

    return {
        "current_pod_count": len(matched_pods),

        "pod_cpu_usage_percent_avg": safe_avg(
            [p.get("pod_cpu_usage_percent_avg", 0.0) for p in matched_pods]
        ),

        "pod_cpu_usage_percent_p95": p95(
            [p.get("pod_cpu_usage_percent_p95", 0.0) for p in matched_pods]
        ),

        "pod_memory_usage_mb_avg": safe_avg(
            [p.get("pod_memory_usage_mb_avg", 0.0) for p in matched_pods]
        ),

        "pod_memory_usage_mb_p95": p95(
            [p.get("pod_memory_usage_mb_p95", 0.0) for p in matched_pods]
        ),

        "pod_restart_count": sum(
            p.get("pod_restart_count", 0.0) for p in matched_pods
        ),

        "pod_cpu_limit_percent": max(
            p.get("pod_cpu_limit_percent", 0.0) for p in matched_pods
        ),

        "pod_memory_limit_percent": max(
            p.get("pod_memory_limit_percent", 0.0) for p in matched_pods
        ),
    }
