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


---

# 🔧 Setup Guide

## 1️⃣ Check Python Version

```bash
python --version

2️⃣ Create Virtual Environment

python -m venv venv

3️⃣ Activate Virtual Environment

venv\Scripts\activate

4️⃣ Install Required Libraries

pip install requests networkx boto3 pytest matplotlib python-dateutil

If pip upgrade is required:
python -m pip install --upgrade pip

Verify installation:
pip list

▶️ Run the Pipeline

Activate the virtual environment:
venv\Scripts\activate

Run the full collector pipeline:
python main.py

Run a single collector (example):
python collectors/node/node_cpu_collector.py

📂 Dataset Output
Type	                Location
CSV Dataset	            output/dataset/metrics_dataset.csv
JSON Lines Dataset	    output/dataset/metrics_dataset.jsonl
Raw Prometheus Dumps	output/raw/

Run Tests

Run all tests:
pytest -q

Kubernetes + Prometheus Commands

Port-forward Prometheus:
kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

Get Pods:
kubectl get pods -o wide

Get Services:
kubectl get svc -n default

Apply Deployment YAML:
kubectl apply -f src/store-admin/service.yaml

Restart Deployment:
kubectl rollout restart deploy store-front

Delete Deployments:
kubectl delete -f mesh-metrics-test.yaml
kubectl delete -f tests/istio/mesh-traffic-generator.yaml

Check Traffic Generator Pod:
kubectl get pods -n default | findstr mesh-traffic-generator

🔀 Switch Between Local & AKS Context

kubectl config use-context docker-desktop
kubectl config use-context sr-research-aks

Verify:
kubectl config current-context


🌐 API Service

Start FastAPI (Uvicorn):
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
or
python -m uvicorn api.server:app --reload

# API Endpoints — Metrics Collector Backend

| #  | Endpoint | Method | Description | Type |
|----|---------|--------|-------------|------|
| 1  | `/metrics/live` | GET | Fetch one-time snapshot of all metrics | JSON |
| 2  | `/metrics/live-stream` | GET | Stream real-time metrics (SSE) | 🔴 Stream |
| 3  | `/process/live` | GET | Get live system process info | JSON |
| 4  | `/process/live-stream` | GET | Stream live process info (SSE) | 🔴 Stream |
| 5  | `/performance/live-stream` | GET | Stream cluster performance metrics | 🔴 Stream |
| 6  | `/nodes/live-stream` | GET | Stream **Node-level** metrics | 🔴 Stream |
| 7  | `/pods/live-stream` | GET | Stream **Pod-level** metrics | 🔴 Stream |
| 8  | `/apps/live-stream` | GET | Stream **Application-level** metrics | 🔴 Stream |
| 9  | `/mesh/live-stream` | GET | Stream **Service Mesh / Istio** metrics | 🔴 Stream |
| 10 | `/graph/centrality/live-stream` | GET | Stream **Graph Centrality** metrics (Novelty) | 🔴 Stream |
| 11 | `/stress-index/live-stream` | GET | Stream **Stress Index + Scaling Signals** | 🔴 Stream |
| 12 | `/config/runtime` | GET | Get runtime config (active values) | JSON |
| 13 | `/config/targets` | GET | Get Prometheus & scrape targets config | JSON |
| 14 | `/config/metrics` | GET | Get enabled metrics config | JSON |
| 15 | `/runtime/pods?namespace=default` | GET | List running pods by namespace | JSON |
| 16 | `/runtime/services?namespace=default` | GET | List running services by namespace | JSON |
| 17 | `/runtime/monitoring/services?namespace=monitoring` | GET | List monitoring stack services | JSON |
| 18 | `/timeseries/services/live` | GET | Stream **service timeseries data for ML** | 🔴 Stream |
| 19 | `/resilience/live-stream` | GET | Stream **resilience validation metrics** | 🔴 Stream |


✅ Testable JSON Endpoints

http://localhost:8000/metrics/live
http://localhost:8000/process/live
http://localhost:8000/config/runtime
http://localhost:8000/config/targets
http://localhost:8000/config/metrics
http://localhost:8000/runtime/pods?namespace=default
http://localhost:8000/runtime/services?namespace=default
http://localhost:8000/runtime/monitoring/services?namespace=monitoring

🔴 Streaming (SSE) Endpoints

http://localhost:8000/metrics/live-stream
http://localhost:8000/process/live-stream
http://localhost:8000/performance/live-stream
http://localhost:8000/nodes/live-stream
http://localhost:8000/pods/live-stream
http://localhost:8000/apps/live-stream
http://localhost:8000/mesh/live-stream
http://localhost:8000/graph/centrality/live-stream
http://localhost:8000/stress-index/live-stream
http://localhost:8000/timeseries/services/live
http://localhost:8000/resilience/live-stream




Test Modes (Optional)

Run with Queue Injection Test:
$env:QUEUE_TEST_MODE="1"
python main.py

Error Testing:
$env:ERROR_TEST_MODE="1"
$env:QUEUE_TEST_MODE="1"
python main.py

Custom Window Test:
$env:WINDOW_SIZE_SECONDS="60"
$env:SCRAPE_INTERVAL_SECONDS="99999"
python main.py
