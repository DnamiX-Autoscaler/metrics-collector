import json
import time

from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities

from utils.time_utils import current_utc_iso
from config.settings import WINDOW_SIZE_SECONDS
from api.service_targets import NAMESPACE_SERVICES


def generate_resilience_metrics():
    """
    REAL-TIME RESILIENCE METRICS STREAM (SSE)

    Uses:
      - App metrics
      - Pod metrics
      - Service mesh metrics
      - Graph centrality (novelty)

    Output format matches Component-3 / ML / Scaling input
    """

    while True:
        services_payload = []

        for namespace, services in NAMESPACE_SERVICES.items():

            # Graph centrality (novel contribution)
            centrality_map = compute_all_centralities(
                namespace,
                WINDOW_SIZE_SECONDS
            )

            # Pod metrics (namespace-wide)
            pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            for service in services:

                # ---------------- APP ----------------
                app = collect_app_metrics(namespace, service, WINDOW_SIZE_SECONDS)

                # ---------------- POD ----------------
                pods_for_service = {
                    p: m for p, m in pod_map.items()
                    if p.startswith(service)
                }

                pod_count = len(pods_for_service)

                restart_count = sum(
                    m.get("pod_restart_count", 0)
                    for m in pods_for_service.values()
                )

                cpu_percent = sum(
                    m.get("pod_cpu_usage_percent_avg", 0)
                    for m in pods_for_service.values()
                ) / max(pod_count, 1)

                mem_percent = sum(
                    m.get("pod_memory_limit_percent", 0)
                    for m in pods_for_service.values()
                ) / max(pod_count, 1)

                # ---------------- MESH ----------------
                mesh = collect_mesh_metrics(namespace, service, WINDOW_SIZE_SECONDS)

                # ---------------- CENTRALITY ----------------
                centrality = centrality_map.get(service, {})

                services_payload.append({
                    "deployment": service,
                    "request_pods": pod_count,
                    "timestamp": current_utc_iso(),
                    "metrics": {
                        # App-level resilience
                        "success_rate": app.get("success_rate_percent", 1.0),
                        "error_rate": app.get("error_rate_percent", 0.0),
                        "p95_latency_before": app.get("latency_p95_ms", 0.0),
                        "p95_latency_after": mesh.get("mesh_latency_p95_ms", 0.0),

                        # Resource pressure
                        "cpu_percent": round(cpu_percent, 2),
                        "mem_percent": round(mem_percent, 2),
                        "restart_count": restart_count,

                        # Traffic recovery (mesh-based)
                        "traffic_recovery": (
                            mesh.get("inbound_request_rate_rps", 0.0) /
                            max(app.get("request_rate_rps", 1.0), 1.0)
                        ),

                        # Graph centrality (novelty)
                        "degree_centrality": centrality.get("degree_centrality", 0.0),
                        "betweenness_centrality": centrality.get("betweenness_centrality", 0.0),
                        "closeness_centrality": centrality.get("closeness_centrality", 0.0),
                        "eigenvector_centrality": centrality.get("eigenvector_centrality", 0.0),
                    }
                })

        yield f"data: {json.dumps({'services': services_payload})}\n\n"
        time.sleep(2)
