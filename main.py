# main.py

import os
import time
from typing import Dict, Any, List

from config.settings import (
    PROMETHEUS_URL,
    CLUSTER_ID,
    OUTPUT_DATASET_PATH,
    discover_namespaces,
    discover_services,
)
from config.constants import WINDOW_SIZE_SECONDS, SCRAPE_INTERVAL_SECONDS

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics

from graph_centrality.compute_all import compute_all_centralities

from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row

from exporters.csv_exporter import append_row_to_csv
from exporters.json_exporter import append_row_to_jsonl

from utils.time_utils import current_utc_iso
from utils.logger import get_logger

logger = get_logger("main")

RAW_OUTPUT_DIR = "output/raw"
DATASET_DIR = "output/dataset"
os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)

CSV_DATASET_FILE = os.path.join(DATASET_DIR, OUTPUT_DATASET_PATH)
JSONL_DATASET_FILE = CSV_DATASET_FILE[:-4] + ".jsonl" if CSV_DATASET_FILE.endswith(".csv") else CSV_DATASET_FILE + ".jsonl"


def _pick_representative_node(node_metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """
    Docker Desktop / single-node normalization.
    """
    if not node_metrics:
        return {}

    first_key = next(iter(node_metrics.keys()))
    metrics = dict(node_metrics[first_key])
    metrics["node_name"] = os.getenv("FORCE_NODE_NAME", "docker-desktop")
    return metrics


def _aggregate_pods_for_service(service_name: str, pod_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Filter pods by prefix match: pod.startswith(service_name)
    If not found -> fallback all pods (namespace aggregate)
    """
    if not pod_metrics:
        return {
            "current_pod_count": 0,
            "pod_cpu_usage_percent_avg": 0.0,
            "pod_cpu_usage_percent_p95": 0.0,
            "pod_memory_usage_mb_avg": 0.0,
            "pod_memory_usage_mb_p95": 0.0,
            "pod_restart_count": 0.0,
            "pod_cpu_limit_percent": 0.0,
            "pod_memory_limit_percent": 0.0,
        }

    selected = {pod: vals for pod, vals in pod_metrics.items() if pod.startswith(service_name)}
    if not selected:
        selected = pod_metrics

    pod_count = len(selected)

    def avg_for_key(key: str) -> float:
        vals: List[float] = []
        for m in selected.values():
            v = m.get(key)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        return sum(vals) / len(vals) if vals else 0.0

    return {
        "current_pod_count": float(pod_count),
        "pod_cpu_usage_percent_avg": avg_for_key("pod_cpu_usage_percent_avg"),
        "pod_cpu_usage_percent_p95": avg_for_key("pod_cpu_usage_percent_p95"),
        "pod_memory_usage_mb_avg": avg_for_key("pod_memory_usage_mb_avg"),
        "pod_memory_usage_mb_p95": avg_for_key("pod_memory_usage_mb_p95"),
        "pod_restart_count": avg_for_key("pod_restart_count"),
        "pod_cpu_limit_percent": avg_for_key("pod_cpu_limit_percent"),
        "pod_memory_limit_percent": avg_for_key("pod_memory_limit_percent"),
    }


def scrape_and_build_rows() -> None:
    loop_timestamp = current_utc_iso()
    window_start_ts = time.time() - WINDOW_SIZE_SECONDS

    logger.info("==== SCRAPE START @ %s ====", loop_timestamp)

    # 1) Node metrics (cluster level)
    node_metrics_map = collect_node_metrics(
        window_start_ts=window_start_ts,
        window_size_seconds=WINDOW_SIZE_SECONDS,
    )
    representative_node = _pick_representative_node(node_metrics_map)

    # Discover namespaces at runtime
    namespaces = discover_namespaces()
    logger.info("Namespaces (runtime): %s", namespaces)

    for namespace in namespaces:
        logger.info("Processing namespace=%s", namespace)

        # Discover services for this namespace at runtime
        services_in_ns = discover_services(namespace)
        logger.info("Services in %s: %s", namespace, services_in_ns)

        if not services_in_ns:
            logger.warning("No services discovered in namespace=%s. Skipping.", namespace)
            continue

        # 2) Graph centrality (for this namespace)
        centrality_map = compute_all_centralities(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
            min_rps_threshold=0.01,
        )

        # 3) Pod metrics (namespace-wide)
        pod_metrics_map = collect_pod_metrics(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
        )

        # 4) Per service
        for service_name in services_in_ns:
            logger.info("Collecting metrics for %s/%s", namespace, service_name)

            pod_metrics_for_service = _aggregate_pods_for_service(service_name, pod_metrics_map)

            app_metrics = collect_app_metrics(
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
            )

            mesh_metrics = collect_mesh_metrics(
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
            )

            merged_metrics = merge_metrics(
                base={},
                node_metrics=representative_node,
                pod_metrics=pod_metrics_for_service,
                app_metrics=app_metrics,
                mesh_metrics=mesh_metrics,
                stress_metrics=None,
                centrality_metrics=None,
                scaling_decision=None,
            )

            centrals = centrality_map.get(service_name, {
                "degree_centrality": 0.0,
                "betweenness_centrality": 0.0,
                "closeness_centrality": 0.0,
                "eigenvector_centrality": 0.0,
            })

            scaling_decision = {
                "current_replicas": int(merged_metrics.get("current_pod_count", 1) or 1),
                "recommended_replicas": int(merged_metrics.get("current_pod_count", 1) or 1),
                "scale_direction": "NONE",
            }

            row = build_dataset_row(
                cluster_id=CLUSTER_ID,
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
                merged_metrics=merged_metrics,
                centrality_for_service=centrals,
                scaling_decision=scaling_decision,
                timestamp=loop_timestamp,
            )

            append_row_to_csv(CSV_DATASET_FILE, row)
            append_row_to_jsonl(JSONL_DATASET_FILE, row)

            logger.info("Dataset row saved for %s/%s", namespace, service_name)

    logger.info("==== SCRAPE END ====")


def run_pipeline() -> None:
    logger.info("Starting metrics collector pipeline…")
    logger.info("Prometheus URL: %s", PROMETHEUS_URL)
    logger.info("Cluster ID: %s", CLUSTER_ID)

    while True:
        try:
            scrape_and_build_rows()
        except Exception as e:
            logger.exception("Error during scrape cycle: %s", e)

        logger.info("Sleeping %ds before next scrape…", SCRAPE_INTERVAL_SECONDS)
        time.sleep(SCRAPE_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_pipeline()
