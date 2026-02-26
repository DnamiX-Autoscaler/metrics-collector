import json
import time
from typing import Dict, Any, List
from collections import deque

from stress_index.stress_index_aggregator import compute_stress_index
from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from processors.data_merger import merge_metrics
from utils.time_utils import current_utc_iso
from config.settings import WINDOW_SIZE_SECONDS
from api.service_targets import NAMESPACE_SERVICES

HISTORY_SIZE = 6
history_buffer = deque(maxlen=HISTORY_SIZE)


def aggregate_pod_metrics_for_service(
    pod_map: Dict[str, Dict[str, Any]],
    service_name: str
) -> Dict[str, float]:
    """
    Aggregate pod metrics for a service using pod-name prefix match
    """

    service_pods = [
        m for pod, m in pod_map.items()
        if pod.startswith(service_name)
    ]

    if not service_pods:
        return {}

    def avg(key):
        vals = [p.get(key, 0.0) for p in service_pods]
        return sum(vals) / len(vals) if vals else 0.0

    def maxv(key):
        vals = [p.get(key, 0.0) for p in service_pods]
        return max(vals) if vals else 0.0

    return {
        "current_pod_count": len(service_pods),
        "pod_cpu_usage_percent_p95": maxv("pod_cpu_usage_percent_p95"),
        "pod_cpu_limit_percent": avg("pod_cpu_limit_percent"),
        "pod_memory_usage_mb_p95": maxv("pod_memory_usage_mb_p95"),
        "pod_memory_limit_percent": avg("pod_memory_limit_percent"),
    }


def generate_stress_index_stream():

    while True:
        services: List[Dict[str, Any]] = []
        stress_values = []
        scale_up = scale_down = stable = 0
        idx = 0

        # ---- NODE (shared across all namespaces) ----
        node_map = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
        node_metrics = list(node_map.values())[0] if node_map else {}

        for namespace, svc_list in NAMESPACE_SERVICES.items():

            # ---- POD MAP (once per namespace) ----
            pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            for svc in svc_list:
                idx += 1

                pod_metrics = aggregate_pod_metrics_for_service(pod_map, svc)
                app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
                mesh = collect_mesh_metrics(namespace, svc, WINDOW_SIZE_SECONDS)

                merged = merge_metrics(
                    base={},
                    node_metrics=node_metrics,
                    pod_metrics=pod_metrics,
                    app_metrics=app,
                    mesh_metrics=mesh,
                )

                stress = compute_stress_index(merged)
                stress_index = round(stress["stress_index"], 3)
                stress_values.append(stress_index)

                current_replicas = pod_metrics.get("current_pod_count", 1)

                # ---- Scaling Logic ----
                if stress_index > 0.7:
                    recommended = current_replicas + 2
                    direction = "up"
                    scale_up += 1
                elif stress_index < 0.35:
                    recommended = max(1, current_replicas - 1)
                    direction = "down"
                    scale_down += 1
                else:
                    recommended = current_replicas
                    direction = "stable"
                    stable += 1

                services.append({
                    "id": idx,
                    "timestamp": current_utc_iso(),
                    "namespace": namespace,
                    "service_name": svc,
                    "name": svc.replace("-", " ").title(),
                    "cpu_pressure_index": round(stress["cpu_pressure_index"], 3),
                    "memory_pressure_index": round(stress["memory_pressure_index"], 3),
                    "io_pressure_index": round(stress["io_pressure_index"], 3),
                    "stress_index": stress_index,
                    "current_replicas": current_replicas,
                    "recommended_replicas": recommended,
                    "scale_direction": direction,
                })

        # ---- HISTORICAL ----
        if stress_values:
            history_buffer.append({
                "timestamp": current_utc_iso(),
                "cpu_pressure_avg": round(
                    sum(s["cpu_pressure_index"] for s in services) / len(services), 3
                ),
                "memory_pressure_avg": round(
                    sum(s["memory_pressure_index"] for s in services) / len(services), 3
                ),
                "io_pressure_avg": round(
                    sum(s["io_pressure_index"] for s in services) / len(services), 3
                ),
                "stress_avg": round(sum(stress_values) / len(stress_values), 3),
            })

        insights = {
            "high_pressure_services": scale_up,
            "scale_up_needed": scale_up,
            "scale_down_needed": scale_down,
            "stable_services": stable,
            "avg_stress_index": round(
                sum(stress_values) / len(stress_values), 3
            ) if stress_values else 0.0,
        }

        payload = {
            "services": services,
            "historical": list(history_buffer),
            "insights": insights,
        }

        yield f"data: {json.dumps(payload)}\n\n"
        time.sleep(3)
