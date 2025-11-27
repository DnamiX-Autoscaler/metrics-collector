# main.py

import os
import time
from typing import Dict, Any, List, Tuple

from config.settings import (
    PROMETHEUS_URL,
    CLUSTER_ID,
    TARGET_NAMESPACES,
    TARGET_SERVICES,
    OUTPUT_DATASET_PATH,
)
from config.constants import WINDOW_SIZE_SECONDS, SCRAPE_INTERVAL_SECONDS

from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from collectors.app.app_aggregator import collect_app_metrics
from collectors.mesh.mesh_aggregator import collect_mesh_metrics

from graph_centrality.compute_all import compute_all_centralities

from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row, DATASET_COLUMNS

from exporters.csv_exporter import append_row_to_csv
from exporters.json_exporter import append_row_to_jsonl

from utils.time_utils import current_utc_iso
from utils.logger import get_logger

logger = get_logger("main")

# -------------------------------------------------------------------
# OUTPUT DIRS
# -------------------------------------------------------------------
RAW_OUTPUT_DIR = "output/raw"
DATASET_DIR = "output/dataset"

os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)

# CSV / JSONL file paths (use OUTPUT_DATASET_PATH as base)
CSV_DATASET_FILE = os.path.join(DATASET_DIR, OUTPUT_DATASET_PATH)
if CSV_DATASET_FILE.endswith(".csv"):
    JSONL_DATASET_FILE = CSV_DATASET_FILE[:-4] + ".jsonl"
else:
    JSONL_DATASET_FILE = CSV_DATASET_FILE + ".jsonl"


# -------------------------------------------------------------------
# INTERNAL HELPERS
# -------------------------------------------------------------------

def _pick_representative_node(node_metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """
    Fix for Docker Desktop / single-node clusters:
    Prometheus gives instance keys like:
        "192.168.65.3:10250"
    But dataset expects stable node names like:
        "docker-desktop"

    So we normalize ALL node metrics to:
        node_name = "docker-desktop"
    """

    if not node_metrics:
        return {}

    # pick first entry
    first_key = next(iter(node_metrics.keys()))
    metrics = dict(node_metrics[first_key])

    # force consistent node name
    metrics["node_name"] = "docker-desktop"

    return metrics


def _aggregate_pods_for_service(
    service_name: str,
    pod_metrics: Dict[str, Dict[str, float]],
) -> Dict[str, float]:
    """
    pod_metrics dict (from pod_aggregator):
      {
        "product-service-xxxxx": { ... },
        "order-service-yyyyy": { ... },
        ...
      }

    - Try to filter pods whose name startswith service_name.
    - If none match, fall back to using ALL pods in namespace.
    - For each numeric field, compute average across selected pods.
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

    # Filter pods belonging to this service (by name prefix)
    selected: Dict[str, Dict[str, float]] = {
        pod: vals for pod, vals in pod_metrics.items()
        if pod.startswith(service_name)
    }

    # If nothing matched, fallback to all pods (namespace-level aggregate)
    if not selected:
        selected = pod_metrics

    pod_count = len(selected)

    def avg_for_key(key: str) -> float:
        vals: List[float] = []
        for m in selected.values():
            v = m.get(key)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    aggregated = {
        "current_pod_count": float(pod_count),
        "pod_cpu_usage_percent_avg": avg_for_key("pod_cpu_usage_percent_avg"),
        "pod_cpu_usage_percent_p95": avg_for_key("pod_cpu_usage_percent_p95"),
        "pod_memory_usage_mb_avg": avg_for_key("pod_memory_usage_mb_avg"),
        "pod_memory_usage_mb_p95": avg_for_key("pod_memory_usage_mb_p95"),
        "pod_restart_count": avg_for_key("pod_restart_count"),
        "pod_cpu_limit_percent": avg_for_key("pod_cpu_limit_percent"),
        "pod_memory_limit_percent": avg_for_key("pod_memory_limit_percent"),
    }

    return aggregated


# -------------------------------------------------------------------
# MAIN SCRAPE FOR ONE ITERATION
# -------------------------------------------------------------------

def scrape_and_build_rows() -> None:
    """
    One full scrape cycle:
      - Node metrics (cluster level)
      - For each namespace:
          - Graph centrality (degree / betweenness / closeness / eigenvector)
          - Pod metrics (namespace → filtered per service by pod name)
          - For each service:
              - App metrics (RPS / latency / errors / queue)
              - Mesh metrics (ingress / egress / latency / retries / TLS errors)
              - Merge + build dataset row
              - Export to CSV + JSONL
    """

    loop_timestamp = current_utc_iso()
    window_start_ts = time.time() - WINDOW_SIZE_SECONDS

    logger.info("==== SCRAPE START @ %s ====", loop_timestamp)

    # ---------------------------------------------------------------
    # 1) NODE METRICS (cluster level)
    # ---------------------------------------------------------------
    node_metrics_map = collect_node_metrics(
        window_start_ts=window_start_ts,
        window_size_seconds=WINDOW_SIZE_SECONDS,
    )
    representative_node = _pick_representative_node(node_metrics_map)

    # ---------------------------------------------------------------
    # FOR EACH NAMESPACE
    # ---------------------------------------------------------------
    for namespace in TARGET_NAMESPACES:
        logger.info("Processing namespace=%s", namespace)

        # 2) GRAPH CENTRALITY (your novelty)
        centrality_map = compute_all_centralities(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
            min_rps_threshold=0.01,
        )

        # 3) POD METRICS (namespace-wide, aggregated per service later)
        pod_metrics_map = collect_pod_metrics(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
        )

        # -----------------------------------------------------------
        # FOR EACH SERVICE IN THIS NAMESPACE
        # -----------------------------------------------------------
        for service_name in TARGET_SERVICES:
            logger.info("Collecting metrics for %s/%s", namespace, service_name)

            # 3a) Aggregate pod metrics for this service
            pod_metrics_for_service = _aggregate_pods_for_service(
                service_name=service_name,
                pod_metrics=pod_metrics_map,
            )

            # 3b) APP METRICS (Prometheus client / app-level)
            app_metrics = collect_app_metrics(
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
            )

            # 3c) MESH METRICS (Istio)
            mesh_metrics = collect_mesh_metrics(
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
            )

            # 3d) Merge all metric layers
            merged_metrics = merge_metrics(
                base={},
                node_metrics=representative_node,
                pod_metrics=pod_metrics_for_service,
                app_metrics=app_metrics,
                mesh_metrics=mesh_metrics,
                stress_metrics=None,          # dataset_row_builder will calc stress_index
                centrality_metrics=None,      # centrality is passed separately
                scaling_decision=None,        # scaling decision passed separately
            )

            # 3e) Centrality for THIS service
            centrals = centrality_map.get(service_name, {
                "degree_centrality": 0.0,
                "betweenness_centrality": 0.0,
                "closeness_centrality": 0.0,
                "eigenvector_centrality": 0.0,
            })

            # 3f) Placeholder scaling decision (Component 2 will replace)
            scaling_decision = {
                "current_replicas": merged_metrics.get("current_pod_count", 1),
                "recommended_replicas": merged_metrics.get("current_pod_count", 1),
                "scale_direction": "NONE",
            }

            # 3g) Build final dataset row
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

            # 3h) Export
            append_row_to_csv(CSV_DATASET_FILE, row)
            append_row_to_jsonl(JSONL_DATASET_FILE, row)

            logger.info("Dataset row saved for %s/%s", namespace, service_name)

    logger.info("==== SCRAPE END ====")


# -------------------------------------------------------------------
# MAIN LOOP
# -------------------------------------------------------------------

def run_pipeline() -> None:
    """
    Infinite loop – call scrape_and_build_rows() every SCRAPE_INTERVAL_SECONDS.
    """

    logger.info("Starting metrics collector pipeline…")
    logger.info("Prometheus URL: %s", PROMETHEUS_URL)
    logger.info("Cluster ID: %s", CLUSTER_ID)
    logger.info("Namespaces: %s", TARGET_NAMESPACES)
    logger.info("Services: %s", TARGET_SERVICES)

    while True:
        try:
            scrape_and_build_rows()
        except Exception as e:
            logger.exception("Error during scrape cycle: %s", e)

        logger.info("Sleeping %ds before next scrape…", SCRAPE_INTERVAL_SECONDS)
        time.sleep(SCRAPE_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_pipeline()
