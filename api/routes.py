# api/routes.py

from fastapi import APIRouter
from typing import Dict, Any

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities
from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row
from config.settings import TARGET_SERVICES, TARGET_NAMESPACES, WINDOW_SIZE_SECONDS, CLUSTER_ID

router = APIRouter()


@router.get("/metrics/live")
def get_live_metrics() -> Dict[str, Any]:

    response = {}

    for namespace in TARGET_NAMESPACES:
        for svc in TARGET_SERVICES:

            # 1. Node metrics
            node = collect_node_metrics(
                window_start_ts=0,
                window_size_seconds=WINDOW_SIZE_SECONDS
            )

            # 2. Pod metrics
            pod = collect_pod_metrics(
                namespace=namespace,
                window_size_seconds=WINDOW_SIZE_SECONDS
            )

            # 3. App metrics
            app = collect_app_metrics(
                namespace=namespace,
                service_name=svc,
                window_size_seconds=WINDOW_SIZE_SECONDS
            )

            # 4. Mesh metrics
            mesh = collect_mesh_metrics(
                namespace=namespace,
                service_name=svc,
                window_size_seconds=WINDOW_SIZE_SECONDS
            )

            # 5. Centrality
            centrality_map = compute_all_centralities(namespace, WINDOW_SIZE_SECONDS)
            centrality = centrality_map.get(svc, {})

            # 6. merge
            merged = merge_metrics(
                base={},
                node_metrics=list(node.values())[0] if node else {},
                pod_metrics=pod.get(svc, {}),
                app_metrics=app,
                mesh_metrics=mesh,
                centrality_metrics=centrality
            )

            # 7. Final row format
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
