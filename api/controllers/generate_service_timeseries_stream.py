import json
import time
from datetime import datetime

from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities
from processors.data_merger import merge_metrics
from utils.time_features import compute_time_features
from utils.time_utils import current_utc_iso
from config.settings import TARGET_SERVICES, TARGET_NAMESPACES, WINDOW_SIZE_SECONDS
from utils.pod_service_mapper import aggregate_pods_for_service


def generate_service_timeseries_stream():
    """
    SSE stream:
    One ML-ready time-series point per service per tick
    """

    while True:
        response = {}

        for namespace in TARGET_NAMESPACES:
            # compute once per namespace
            centrality_map = compute_all_centralities(
                namespace,
                WINDOW_SIZE_SECONDS
            )

            pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            for svc in TARGET_SERVICES:
                # collect per-service metrics
                app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
                mesh = collect_mesh_metrics(namespace, svc, WINDOW_SIZE_SECONDS)

                # ✅ FIX: pod_map exists here
                pod_metrics = aggregate_pods_for_service(pod_map, svc)
                centrality = centrality_map.get(svc, {})

                merged = merge_metrics(
                    base={},
                    pod_metrics=pod_metrics,
                    app_metrics=app,
                    mesh_metrics=mesh,
                    centrality_metrics=centrality,
                )

                now = datetime.utcnow()
                time_features = compute_time_features(now)

                row = {
                    "timestamp": current_utc_iso(),
                    "service_id": svc,
                    "current_pod_count": merged.get("current_pod_count", 1),

                    # APP
                    "request_rate_rps": merged.get("request_rate_rps", 0.0),
                    "latency_p50_ms": merged.get("latency_p50_ms", 0.0),
                    "latency_p95_ms": merged.get("latency_p95_ms", 0.0),
                    "error_rate_percent": merged.get("error_rate_percent", 0.0),
                    "queue_length": merged.get("queue_length", 0.0),

                    # POD
                    "pod_cpu_usage_percent_avg": merged.get("pod_cpu_usage_percent_avg", 0.0),
                    "pod_cpu_usage_percent_p95": merged.get("pod_cpu_usage_percent_p95", 0.0),
                    "pod_memory_usage_mb_avg": merged.get("pod_memory_usage_mb_avg", 0.0),
                    "pod_memory_usage_mb_p95": merged.get("pod_memory_usage_mb_p95", 0.0),

                    # MESH
                    "mesh_inbound_rps": merged.get("inbound_request_rate_rps", 0.0),
                    "mesh_inbound_latency_p95": merged.get("mesh_latency_p95_ms", 0.0),
                    "mesh_inbound_error_rate": merged.get("mesh_retry_rate_rps", 0.0),

                    # GRAPH
                    "degree_centrality": centrality.get("degree_centrality", 0.0),
                    "eigenvector_centrality": centrality.get("eigenvector_centrality", 0.0),
                    "betweenness_centrality": centrality.get("betweenness_centrality", 0.0),
                    "closeness_centrality": centrality.get("closeness_centrality", 0.0),

                    # TIME FEATURES
                    **time_features,
                }

                response[svc] = {
                    "service_id": svc,
                    "data": [row],
                }

        yield f"data: {json.dumps(response)}\n\n"
        time.sleep(2)
