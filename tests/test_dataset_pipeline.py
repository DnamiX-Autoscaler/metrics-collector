# tests/test_dataset_pipeline.py

from processors.dataset_row_builder import (
    build_dataset_row,
    DATASET_COLUMNS,
)


def test_dataset_row_builder_minimal():
    cluster_id = "cluster-demo"
    namespace = "demo-ns"
    service_name = "product-service"
    window_size = 60

    merged_metrics = {
        "node_name": "node-1",
        "node_cpu_usage_percent": 55.0,
        "node_memory_usage_percent": 70.0,
        "node_memory_usage_mb": 2048.0,
        "node_network_rx_kbps": 120.0,
        "node_network_tx_kbps": 80.0,
        "node_disk_read_iops": 100.0,
        "node_disk_write_iops": 50.0,

        "current_pod_count": 3,
        "pod_cpu_usage_percent_avg": 40.0,
        "pod_cpu_usage_percent_p95": 80.0,
        "pod_memory_usage_mb_avg": 256.0,
        "pod_memory_usage_mb_p95": 512.0,
        "pod_restart_count": 1,
        "pod_cpu_limit_percent": 100.0,
        "pod_memory_limit_percent": 800.0,

        "request_rate_rps": 25.0,
        "success_rate_percent": 99.0,
        "error_rate_percent": 1.0,
        "http_4xx_rate_percent": 0.5,
        "http_5xx_rate_percent": 0.5,
        "latency_p50_ms": 20.0,
        "latency_p95_ms": 50.0,
        "latency_p99_ms": 80.0,
        "queue_length": 5,
        "application_saturation_percent": 30.0,

        "inbound_request_rate_rps": 30.0,
        "outbound_request_rate_rps": 20.0,
        "mesh_latency_p95_ms": 45.0,
        "mesh_retry_rate_rps": 0.2,
        "mesh_tcp_open_connections": 50.0,
        "mesh_tls_error_rate_percent": 0.1,
    }

    centrality_for_service = {
        "degree_centrality": 0.6,
        "betweenness_centrality": 0.2,
        "closeness_centrality": 0.5,
        "eigenvector_centrality": 0.7,
    }

    scaling_decision = {
        "current_replicas": 3,
        "recommended_replicas": 5,
        "scale_direction": "SCALE_UP",
    }

    row = build_dataset_row(
        cluster_id=cluster_id,
        namespace=namespace,
        service_name=service_name,
        window_size_seconds=window_size,
        merged_metrics=merged_metrics,
        centrality_for_service=centrality_for_service,
        scaling_decision=scaling_decision,
        timestamp="2025-01-01T00:00:00Z",
    )

    # All columns must exist
    for col in DATASET_COLUMNS:
        assert col in row

    # Check some semantic values
    assert row["cluster_id"] == cluster_id
    assert row["namespace"] == namespace
    assert row["service_name"] == service_name
    assert row["current_replicas"] == 3
    assert row["recommended_replicas"] == 5
    assert row["scale_direction"] == "SCALE_UP"

    # Stress index fields should be computed (not just 0)
    assert row["cpu_pressure_index"] >= 0.0
    assert row["stress_index"] >= 0.0
