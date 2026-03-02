from typing import Dict, Any, List

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from graph_centrality.compute_all import compute_all_centralities
from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row
from utils.pod_service_mapper import aggregate_pods_for_service
from config.settings import (
    WINDOW_SIZE_SECONDS,
    CLUSTER_ID,
    SYSTEM_NAMESPACES,
    discover_services,
)
from utils.k8s_client import get_core_v1_api


def _get_live_namespace_services() -> Dict[str, List[str]]:
    """
    Discover namespaces and their services fresh at call time.
    Falls back to empty dict on any K8s error.
    """
    try:
        v1 = get_core_v1_api()
        all_ns = [n.metadata.name for n in v1.list_namespace().items]
        namespaces = sorted(ns for ns in all_ns if ns not in SYSTEM_NAMESPACES)
    except Exception:
        namespaces = []

    result: Dict[str, List[str]] = {}
    for ns in namespaces:
        try:
            result[ns] = discover_services(ns)
        except Exception:
            result[ns] = []
    return result


def get_live_metrics() -> Dict[str, Any]:
    response = {}

    # Re-discover namespaces + services on every call (avoids stale startup cache)
    namespace_services = _get_live_namespace_services()

    # Node metrics are cluster-wide — collect once
    node_map = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
    node_metrics = list(node_map.values())[0] if node_map else {}

    for namespace, services in namespace_services.items():

        if not services:
            continue

        # Collect once per namespace
        pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)
        centrality_map = compute_all_centralities(namespace, WINDOW_SIZE_SECONDS)

        for svc in services:

            app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
            mesh = collect_mesh_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
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

    return response
