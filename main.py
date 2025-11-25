# main.py

import os
import time
from typing import Dict, Any, List

from config.settings import PROM_URL, CLUSTER_ID, SERVICES, NAMESPACES
from config.constants import WINDOW_SIZE_SECONDS, SCRAPE_INTERVAL_SECONDS

from collectors.node.node_cpu_collector import collect_node_cpu_usage
from collectors.node.node_memory_collector import collect_node_memory
from collectors.node.node_network_collector import collect_node_network
from collectors.node.node_disk_collector import collect_node_disk
from collectors.node.node_aggregator import aggregate_node_metrics

from collectors.pod.pod_cpu_collector import collect_pod_cpu
from collectors.pod.pod_memory_collector import collect_pod_memory
from collectors.pod.pod_restart_collector import collect_pod_restarts
from collectors.pod.pod_limits_collector import collect_pod_limits
from collectors.pod.pod_aggregator import aggregate_pod_metrics

from collectors.app.app_aggregator import collect_app_metrics

from collectors.mesh.mesh_aggregator import collect_mesh_metrics

from graph_centrality.compute_all import compute_all_centralities

from stress_index.stress_index_aggregator import compute_stress_index

from processors.data_cleaner import clean_numeric_fields
from processors.data_merger import merge_metrics
from processors.dataset_row_builder import build_dataset_row
from processors.dataset_row_builder import DATASET_COLUMNS

from exporters.csv_exporter import append_row_to_csv
from exporters.json_exporter import append_row_to_jsonl

from utils.time_utils import current_utc_iso
from utils.logger import get_logger
from utils.http_client import HTTPClient


logger = get_logger("main")

RAW_OUTPUT_DIR = "output/raw"
DATASET_DIR = "output/dataset"

os.makedirs(RAW_OUTPUT_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)


def scrape_single_service(namespace: str, service_name: str) -> Dict[str, Any]:
    """
    Collect all metric layers for a given service.
    """

    logger.info("Scraping metrics for %s/%s", namespace, service_name)

    # ----------------------------
    # 1. NODE-LEVEL METRICS
    # ----------------------------
    node_cpu = collect_node_cpu_usage(namespace, "all-nodes", WINDOW_SIZE_SECONDS)
    node_mem = collect_node_memory(namespace, "all-nodes", WINDOW_SIZE_SECONDS)
    node_net = collect_node_network(namespace, "all-nodes", WINDOW_SIZE_SECONDS)
    node_disk = collect_node_disk(namespace, "all-nodes", WINDOW_SIZE_SECONDS)

    node_metrics = aggregate_node_metrics(
        node_cpu,
        node_mem,
        node_net,
        node_disk,
    )

    # ----------------------------
    # 2. POD-LEVEL METRICS
    # ----------------------------
    pod_cpu = collect_pod_cpu(namespace, service_name, WINDOW_SIZE_SECONDS)
    pod_mem = collect_pod_memory(namespace, service_name, WINDOW_SIZE_SECONDS)
    pod_restart = collect_pod_restarts(namespace, service_name)
    pod_limits = collect_pod_limits(namespace, service_name)

    pod_metrics = aggregate_pod_metrics(
        pod_cpu, pod_mem, pod_restart, pod_limits
    )

    # ----------------------------
    # 3. APP-LEVEL (Prometheus CLIENT LIB)
    # ----------------------------
    app_metrics = collect_app_metrics(
        namespace, service_name, WINDOW_SIZE_SECONDS
    )

    # ----------------------------
    # 4. SERVICE-MESH (ISTIO)
    # ----------------------------
    mesh_metrics = collect_mesh_metrics(
        namespace, service_name, WINDOW_SIZE_SECONDS
    )

    # ----------------------------
    # RETURN RAW LAYERS
    # ----------------------------
    return {
        "node": node_metrics,
        "pod": pod_metrics,
        "app": app_metrics,
        "mesh": mesh_metrics,
    }


def run_pipeline():
    """
    Main loop:
    - Collect metrics for all services
    - Compute graph centrality
    - Build dataset rows
    - Store CSV + JSON
    """

    http = HTTPClient(PROM_URL)

    while True:
        loop_timestamp = current_utc_iso()

        # STEP 1 — Collect metrics for every service
        service_metric_map = {}  # service → merged metrics
        graph_edges = []         # list of (src, dest, weight)

        for namespace in NAMESPACES:
            for service in SERVICES:
                layers = scrape_single_service(namespace, service)

                # merge node+pod+app+mesh
                merged = merge_metrics(
                    base={},
                    node_metrics=layers["node"],
                    pod_metrics=layers["pod"],
                    app_metrics=layers["app"],
                    mesh_metrics=layers["mesh"],
                )

                # record for graph building
                # here mesh metrics usually include inbound/outbound traffic
                src = service
                outbound = merged.get("outbound_request_rate_rps", 0)
                inbound = merged.get("inbound_request_rate_rps", 0)

                # add minimal 1-edge graph:
                if outbound > 0:
                    graph_edges.append((service, "downstream-service", outbound))
                if inbound > 0:
                    graph_edges.append(("upstream-service", service, inbound))

                service_metric_map[(namespace, service)] = merged

        # STEP 2 — Compute centrality on graph
        centrality_map = compute_all_centralities(graph_edges)

        # STEP 3 — Build dataset rows
        for (namespace, service_name), merged_metrics in service_metric_map.items():
            centrals = centrality_map.get(service_name, {
                "degree_centrality": 0,
                "betweenness_centrality": 0,
                "closeness_centrality": 0,
                "eigenvector_centrality": 0,
            })

            # scaling decision placeholder (Component 2)
            scaling = {
                "current_replicas": merged_metrics.get("current_pod_count", 1),
                "recommended_replicas": merged_metrics.get("current_pod_count", 1),  # placeholder
                "scale_direction": "NONE",
            }

            row = build_dataset_row(
                cluster_id=CLUSTER_ID,
                namespace=namespace,
                service_name=service_name,
                window_size_seconds=WINDOW_SIZE_SECONDS,
                merged_metrics=merged_metrics,
                centrality_for_service=centrals,
                scaling_decision=scaling,
                timestamp=loop_timestamp,
            )

            # STEP 4 — Export dataset row
            csv_path = os.path.join(DATASET_DIR, "metrics_dataset.csv")
            jsonl_path = os.path.join(DATASET_DIR, "metrics_dataset.jsonl")

            append_row_to_csv(csv_path, row)
            append_row_to_jsonl(jsonl_path, row)

            logger.info("Row saved for %s/%s", namespace, service_name)

        logger.info("Sleeping %ds before next scrape…", SCRAPE_INTERVAL_SECONDS)
        time.sleep(SCRAPE_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_pipeline()
