# Intelligent Metrics Collection for Predictive Auto-Scaling in Kubernetes  
_Component 1 – A.L. Peiris (IT22566270)_

---

## Overview

This project builds a **multi-layer observability pipeline** for Kubernetes microservices.

It collects metrics from:

- **Node Level** (Node Exporter)
- **Pod Level** (cAdvisor)
- **Application Level** (Prometheus Client Library)
- **Service Mesh Level** (Istio Telemetry)
- **Graph-Based Service Dependency Centrality** (Novelty)
- **Stress Index (CPU, Memory, IO)** → Predict workload pressure  
- **Scaling metadata** (Component 2 → ML model)

Finally, it produces a **clean ML-ready dataset** for predictive auto-scaling research.

---

## Folder Structure

component-1-metrics-collector/
│
├── config/
│   ├── settings.py                    # Prometheus URL, cluster ID, namespaces
│   └── constants.py                   # Window size, query intervals
│
├── utils/
│   ├── http_client.py                 # Requests wrapper
│   ├── time_utils.py                  # Timestamps, windows
│   ├── logger.py                      # Logging
│   └── math_utils.py                  # P95, P99, rate functions
│
├── collectors/
│   ├── node/
│   │   ├── node_cpu_collector.py
│   │   ├── node_memory_collector.py
│   │   ├── node_network_collector.py
│   │   ├── node_disk_collector.py
│   │   └── node_aggregator.py         # Combines node metrics
│   │
│   ├── pod/
│   │   ├── pod_cpu_collector.py
│   │   ├── pod_memory_collector.py
│   │   ├── pod_restart_collector.py
│   │   ├── pod_limits_collector.py
│   │   └── pod_aggregator.py
│   │
│   ├── app/
│   │   ├── rps_collector.py
│   │   ├── error_rate_collector.py
│   │   ├── latency_collector.py
│   │   ├── queue_collector.py
│   │   └── app_aggregator.py
│   │
│   ├── mesh/
│   │   ├── mesh_ingress_traffic.py
│   │   ├── mesh_egress_traffic.py
│   │   ├── mesh_latency_collector.py
│   │   ├── mesh_retry_collector.py
│   │   ├── mesh_tcp_collector.py
│   │   ├── mesh_tls_error_collector.py
│   │   └── mesh_aggregator.py
│
├── graph_centrality/                     # Your novelty lives here 
│   ├── edge_extractor.py                 # Build edges from Istio metrics
│   ├── graph_builder.py                  # Build NetworkX graph
│   ├── degree_centrality.py              # (1) degree
│   ├── betweenness_centrality.py         # (2) betweenness
│   ├── closeness_centrality.py           # (3) closeness
│   ├── eigenvector_centrality.py         # (4) eigenvector
│   ├── compute_all.py                    # Combine all 4
│   └── visualizer.py                     # Optional for graphs
│
├── stress_index/
│   ├── cpu_pressure_index.py
│   ├── memory_pressure_index.py
│   ├── io_pressure_index.py
│   └── stress_index_aggregator.py        # Combines all pressure metrics
│
├── processors/
│   ├── data_cleaner.py                   # Normalize + clean
│   ├── data_merger.py                    # Merge node+pod+mesh+centrality
│   ├── window_aggregator.py              # Sliding window logic
│   └── dataset_row_builder.py            # FINAL dataset row
│
├── exporters/
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── s3_exporter.py                    # Optional
│
├── output/
│   ├── raw/                              # Raw Prometheus dumps
│   └── dataset/                          # Final ML-ready rows
│
├── tests/
│   ├── test_promql_queries.py
│   ├── test_centrality_metrics.py
│   ├── test_stress_index.py
│   └── test_dataset_pipeline.py
│
├── main.py                               # Main pipeline entrypoint
└── README.md                             # Documentation
