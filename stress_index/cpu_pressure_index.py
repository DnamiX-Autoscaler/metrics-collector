# CPI = pod_cpu_usage_percent_p95 / pod_cpu_limit_percent
# stress_index/cpu_pressure_index.py

from typing import Dict

def compute_cpu_pressure_index(metrics: Dict[str, float]) -> float:
    """
    CPU Pressure Index =
        pod_cpu_usage_percent_p95 / (pod_cpu_limit_percent + epsilon)
    """

    usage_p95 = metrics.get("pod_cpu_usage_percent_p95", 0.0)
    cpu_limit = metrics.get("pod_cpu_limit_percent", 100.0)

    if cpu_limit <= 0:
        return 0.0

    return usage_p95 / cpu_limit
