import json
import time

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities
from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row
from utils.pod_service_mapper import aggregate_pods_for_service
from config.settings import (
    TARGET_NAMESPACES,
    WINDOW_SIZE_SECONDS,
    CLUSTER_ID
)
from api.service_targets import TARGET_SERVICES


def generate_live_stream():
    """Continuous real-time metrics generator using SSE."""

    while True:
        response = {}

        for namespace in TARGET_NAMESPACES:

            # collect once per namespace
            node_map = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
            pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)
            centrality_map = compute_all_centralities(namespace, WINDOW_SIZE_SECONDS)

            node_metrics = list(node_map.values())[0] if node_map else {}

            for svc in TARGET_SERVICES:

                app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
                mesh = collect_mesh_metrics(namespace, svc, WINDOW_SIZE_SECONDS)

                # ✅ FIX
                pod_metrics = aggregate_pods_for_service(pod_map, svc)
                centrality = centrality_map.get(svc, {})

                merged = merge_metrics(
                    base={},
                    node_metrics=node_metrics,
                    pod_metrics=pod_metrics,
                    app_metrics=app,
                    mesh_metrics=mesh,
                    centrality_metrics=centrality,
                )

                row = build_dataset_row(
                    cluster_id=CLUSTER_ID,
                    namespace=namespace,
                    service_name=svc,
                    window_size_seconds=WINDOW_SIZE_SECONDS,
                    merged_metrics=merged,
                    centrality_for_service=centrality,
                    scaling_decision={
                        "current_replicas": merged.get("current_pod_count", 1),
                        "recommended_replicas": merged.get("current_pod_count", 1),
                        "scale_direction": "NONE",
                    },
                )

                response[f"{namespace}/{svc}"] = row

        # SSE payload
        yield f"data: {json.dumps(response)}\n\n"
        time.sleep(2)
