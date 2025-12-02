from typing import Dict, Any

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities
from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row
from config.settings import TARGET_SERVICES, TARGET_NAMESPACES, WINDOW_SIZE_SECONDS, CLUSTER_ID


def get_live_metrics() -> Dict[str, Any]:
    response = {}

    for namespace in TARGET_NAMESPACES:
        for svc in TARGET_SERVICES:

            node = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
            pod = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)
            app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
            mesh = collect_mesh_metrics(namespace, svc, WINDOW_SIZE_SECONDS)

            centrality_map = compute_all_centralities(namespace, WINDOW_SIZE_SECONDS)
            centrality = centrality_map.get(svc, {})

            merged = merge_metrics(
                base={},
                node_metrics=list(node.values())[0] if node else {},
                pod_metrics=pod.get(svc, {}),
                app_metrics=app,
                mesh_metrics=mesh,
                centrality_metrics=centrality
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
                }
            )

            response[f"{namespace}/{svc}"] = row

    return response
