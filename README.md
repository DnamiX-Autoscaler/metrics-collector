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

metrics-collector/
│
├── config/
│   ├── settings.py             
│   └── constants.py                   
│
├── utils/
│   ├── http_client.py              
│   ├── time_utils.py            
│   ├── logger.py                      
│   └── math_utils.py                 
│
├── collectors/
│   ├── node/
│   │   ├── node_cpu_collector.py
│   │   ├── node_memory_collector.py
│   │   ├── node_network_collector.py
│   │   ├── node_disk_collector.py
│   │   └── node_aggregator.py       
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
├── graph_centrality/                  
│   ├── edge_extractor.py            
│   ├── graph_builder.py           
│   ├── degree_centrality.py           
│   ├── betweenness_centrality.py    
│   ├── closeness_centrality.py         
│   ├── eigenvector_centrality.py   
│   ├── compute_all.py                  
│   └── visualizer.py       
│
├── stress_index/
│   ├── cpu_pressure_index.py
│   ├── memory_pressure_index.py
│   ├── io_pressure_index.py
│   └── stress_index_aggregator.py  
│
├── processors/
│   ├── data_cleaner.py          
│   ├── data_merger.py            
│   ├── window_aggregator.py     
│   └── dataset_row_builder.py       
│
├── exporters/
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── s3_exporter.py                   
│
├── output/
│   ├── raw/                     
│   └── dataset/                  
│
├── tests/
│   ├── test_promql_queries.py
│   ├── test_centrality_metrics.py
│   ├── test_stress_index.py
│   └── test_dataset_pipeline.py
│
├── main.py                   
└── README.md                       
