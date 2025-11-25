# MPI = pod_memory_usage_mb_p95 / pod_memory_limit_percent
# stress_index/memory_pressure_index.py

from typing import Dict

def compute_memory_pressure_index(metrics: Dict[str, float]) -> float:
    """
    Memory Pressure Index =
        pod_memory_usage_mb_p95 / (pod_memory_limit_percent + epsilon)
    """

    mem_p95 = metrics.get("pod_memory_usage_mb_p95", 0.0)
    mem_limit = metrics.get("pod_memory_limit_percent", 100.0)

    if mem_limit <= 0:
        return 0.0

    return mem_p95 / mem_limit
