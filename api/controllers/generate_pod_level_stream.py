import json
import time
from typing import Dict, Any, List

from collectors.pod.pod_aggregator import collect_pod_metrics
from config.settings import WINDOW_SIZE_SECONDS
from utils.time_utils import current_utc_iso
from utils.pod_service_mapper import aggregate_pods_for_service
from api.service_targets import NAMESPACE_SERVICES


def generate_pod_level_stream():
    """
    SSE generator for real-time POD-LEVEL aggregated metrics.
    One row per namespace → service, with timestamp.
    """

    while True:
        pod_level_rows: List[Dict[str, Any]] = []
        ts = current_utc_iso()

        for namespace, services in NAMESPACE_SERVICES.items():
            pod_metrics_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            if not pod_metrics_map:
                continue

            for service_name in services:
                agg = aggregate_pods_for_service(pod_metrics_map, service_name)

                pod_level_rows.append({
                    "timestamp": ts,
                    "namespace": namespace,
                    "service_name": service_name,
                    "current_pod_count": agg["current_pod_count"],
                    "pod_cpu_usage_percent_avg": round(agg["pod_cpu_usage_percent_avg"], 2),
                    "pod_cpu_usage_percent_p95": round(agg["pod_cpu_usage_percent_p95"], 2),
                    "pod_memory_usage_mb_avg": round(agg["pod_memory_usage_mb_avg"], 2),
                    "pod_memory_usage_mb_p95": round(agg["pod_memory_usage_mb_p95"], 2),
                    "pod_restart_count": int(agg["pod_restart_count"]),
                    "pod_cpu_limit_percent": round(agg["pod_cpu_limit_percent"], 2),
                    "pod_memory_limit_percent": round(agg["pod_memory_limit_percent"], 2),
                })

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(pod_level_rows)}\n\n"

        time.sleep(2)  # refresh interval (seconds)
