import json
import time
from typing import Dict, Any, List

from collectors.pod.pod_aggregator import collect_pod_metrics
from config.settings import TARGET_NAMESPACES, WINDOW_SIZE_SECONDS


def generate_pod_level_stream():
    """
    SSE generator for real-time POD-LEVEL aggregated metrics
    Output shape EXACTLY matches frontend contract
    """

    while True:
        pod_level_rows: List[Dict[str, Any]] = []

        for namespace in TARGET_NAMESPACES:
            pod_metrics_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            if not pod_metrics_map:
                continue

            pod_count = len(pod_metrics_map)

            # ---- Aggregate across all pods in namespace ----
            cpu_avg = []
            cpu_p95 = []
            mem_avg = []
            mem_p95 = []
            restart_sum = []
            cpu_limit = []
            mem_limit = []

            for pod_metrics in pod_metrics_map.values():
                cpu_avg.append(pod_metrics.get("pod_cpu_usage_percent_avg", 0.0))
                cpu_p95.append(pod_metrics.get("pod_cpu_usage_percent_p95", 0.0))
                mem_avg.append(pod_metrics.get("pod_memory_usage_mb_avg", 0.0))
                mem_p95.append(pod_metrics.get("pod_memory_usage_mb_p95", 0.0))
                restart_sum.append(pod_metrics.get("pod_restart_count", 0))
                cpu_limit.append(pod_metrics.get("pod_cpu_limit_percent", 0.0))
                mem_limit.append(pod_metrics.get("pod_memory_limit_percent", 0.0))

            pod_level_rows.append({
                "current_pod_count": pod_count,
                "pod_cpu_usage_percent_avg": round(sum(cpu_avg) / pod_count, 2),
                "pod_cpu_usage_percent_p95": round(max(cpu_p95), 2),
                "pod_memory_usage_mb_avg": round(sum(mem_avg) / pod_count, 2),
                "pod_memory_usage_mb_p95": round(max(mem_p95), 2),
                "pod_restart_count": int(sum(restart_sum)),
                "pod_cpu_limit_percent": round(sum(cpu_limit) / pod_count, 2),
                "pod_memory_limit_percent": round(sum(mem_limit) / pod_count, 2),
            })

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(pod_level_rows)}\n\n"

        time.sleep(2)  # refresh interval (seconds)
