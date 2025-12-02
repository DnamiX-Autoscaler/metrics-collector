# processors/dataset_row_builder.py

from typing import Dict, Any
from utils.time_utils import current_utc_iso
from utils.logger import get_logger
from stress_index.stress_index_aggregator import compute_stress_index

logger = get_logger(__name__)


DATASET_COLUMNS = [
    "timestamp",
    "window_size_seconds",
    "cluster_id",
    "namespace",
    "service_name",

    "node_name",
    "node_cpu_usage_percent",
    "node_memory_usage_percent",
    "node_memory_usage_mb",
    "node_network_rx_kbps",
    "node_network_tx_kbps",
    "node_disk_read_iops",
    "node_disk_write_iops",

    "current_pod_count",
    "pod_cpu_usage_percent_avg",
    "pod_cpu_usage_percent_p95",
    "pod_memory_usage_mb_avg",
    "pod_memory_usage_mb_p95",
    "pod_restart_count",
    "pod_cpu_limit_percent",
    "pod_memory_limit_percent",

    "request_rate_rps",
    "success_rate_percent",
    "error_rate_percent",
    "http_4xx_rate_percent",
    "http_5xx_rate_percent",
    "latency_p50_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "queue_length",
    "application_saturation_percent",

    "inbound_request_rate_rps",
    "outbound_request_rate_rps",
    "mesh_latency_p95_ms",
    "mesh_retry_rate_rps",
    "mesh_tcp_open_connections",
    "mesh_tls_error_rate_percent",

    "degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "eigenvector_centrality",

    "cpu_pressure_index",
    "memory_pressure_index",
    "io_pressure_index",
    "stress_index",

    "current_replicas",
    "recommended_replicas",
    "scale_direction",
]


def build_dataset_row(
    cluster_id: str,
    namespace: str,
    service_name: str,
    window_size_seconds: int,
    merged_metrics: Dict[str, Any],
    centrality_for_service: Dict[str, float],
    scaling_decision: Dict[str, Any],
    timestamp: str | None = None,
) -> Dict[str, Any]:

    ts = timestamp or current_utc_iso()
    stress = compute_stress_index(merged_metrics)

    row = {
        "timestamp": ts,
        "window_size_seconds": window_size_seconds,
        "cluster_id": cluster_id,
        "namespace": namespace,
        "service_name": service_name,

        # NODE
        "node_name": merged_metrics.get("node_name", ""),
        "node_cpu_usage_percent": merged_metrics.get("node_cpu_usage_percent", 0.0),
        "node_memory_usage_percent": merged_metrics.get("node_memory_usage_percent", 0.0),
        "node_memory_usage_mb": merged_metrics.get("node_memory_usage_mb", 0.0),
        "node_network_rx_kbps": merged_metrics.get("node_network_rx_kbps", 0.0),
        "node_network_tx_kbps": merged_metrics.get("node_network_tx_kbps", 0.0),
        "node_disk_read_iops": merged_metrics.get("node_disk_read_iops", 0.0),
        "node_disk_write_iops": merged_metrics.get("node_disk_write_iops", 0.0),

        # POD
        "current_pod_count": merged_metrics.get("current_pod_count", 0.0),
        "pod_cpu_usage_percent_avg": merged_metrics.get("pod_cpu_usage_percent_avg", 0.0),
        "pod_cpu_usage_percent_p95": merged_metrics.get("pod_cpu_usage_percent_p95", 0.0),
        "pod_memory_usage_mb_avg": merged_metrics.get("pod_memory_usage_mb_avg", 0.0),
        "pod_memory_usage_mb_p95": merged_metrics.get("pod_memory_usage_mb_p95", 0.0),
        "pod_restart_count": merged_metrics.get("pod_restart_count", 0.0),
        "pod_cpu_limit_percent": merged_metrics.get("pod_cpu_limit_percent", 0.0),
        "pod_memory_limit_percent": merged_metrics.get("pod_memory_limit_percent", 0.0),

        # APP
        "request_rate_rps": merged_metrics.get("request_rate_rps", 0.0),
        "success_rate_percent": merged_metrics.get("success_rate_percent", 0.0),
        "error_rate_percent": merged_metrics.get("error_rate_percent", 0.0),
        "http_4xx_rate_percent": merged_metrics.get("http_4xx_rate_percent", 0.0),
        "http_5xx_rate_percent": merged_metrics.get("http_5xx_rate_percent", 0.0),
        "latency_p50_ms": merged_metrics.get("latency_p50_ms", 0.0),
        "latency_p95_ms": merged_metrics.get("latency_p95_ms", 0.0),
        "latency_p99_ms": merged_metrics.get("latency_p99_ms", 0.0),
        "queue_length": merged_metrics.get("queue_length", 0.0),
        "application_saturation_percent": merged_metrics.get("application_saturation_percent", 0.0),

        # MESH
        "inbound_request_rate_rps": merged_metrics.get("inbound_request_rate_rps", 0.0),
        "outbound_request_rate_rps": merged_metrics.get("outbound_request_rate_rps", 0.0),
        "mesh_latency_p95_ms": merged_metrics.get("mesh_latency_p95_ms", 0.0),
        "mesh_retry_rate_rps": merged_metrics.get("mesh_retry_rate_rps", 0.0),
        "mesh_tcp_open_connections": merged_metrics.get("mesh_tcp_open_connections", 0.0),
        "mesh_tls_error_rate_percent": merged_metrics.get("mesh_tls_error_rate_percent", 0.0),

        # CENTRALITY
        "degree_centrality": centrality_for_service.get("degree_centrality", 0.0),
        "betweenness_centrality": centrality_for_service.get("betweenness_centrality", 0.0),
        "closeness_centrality": centrality_for_service.get("closeness_centrality", 0.0),
        "eigenvector_centrality": centrality_for_service.get("eigenvector_centrality", 0.0),

        # STRESS INDEX
        "cpu_pressure_index": stress.get("cpu_pressure_index", 0.0),
        "memory_pressure_index": stress.get("memory_pressure_index", 0.0),
        "io_pressure_index": stress.get("io_pressure_index", 0.0),
        "stress_index": stress.get("stress_index", 0.0),

        # SCALING DECISION
        "current_replicas": scaling_decision.get("current_replicas", 0),
        "recommended_replicas": scaling_decision.get("recommended_replicas", 0),
        "scale_direction": scaling_decision.get("scale_direction", "NONE"),
    }

    # Ensure all columns exist
    for col in DATASET_COLUMNS:
        if col not in row:
            row[col] = 0.0

    return row
