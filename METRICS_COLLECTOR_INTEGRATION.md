# 🔗 Metrics Collector Integration Guide
# AutoScaling Microservices Demo + METRICS-COLLECTOR

මේ guide එකෙන් ඔයාගේ METRICS-COLLECTOR backend එක microservices demo එකත් එක්ක connect කරන්නේ කොහොමද කියලා step-by-step explain කරනවා.

---

## 📋 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites Checklist](#2-prerequisites-checklist)
3. [Step 1: Update Metrics Collector Settings](#3-step-1-update-metrics-collector-settings)
4. [Step 2: Start Microservices Demo](#4-step-2-start-microservices-demo)
5. [Step 3: Verify Prometheus Metrics](#5-step-3-verify-prometheus-metrics)
6. [Step 4: Run Metrics Collector](#6-step-4-run-metrics-collector)
7. [Step 5: Generate Load for Training Data](#7-step-5-generate-load-for-training-data)
8. [Step 6: Verify Collected Data](#8-step-6-verify-collected-data)
9. [Kubernetes Deployment](#9-kubernetes-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR LAPTOP / SERVER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              MICROSERVICES DEMO (Docker Compose)              │  │
│  │                                                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │ api-gateway │  │user-service │  │order-service│  ...      │  │
│  │  │  :3000      │  │  :3001      │  │  :3002      │          │  │
│  │  │  /metrics   │  │  /metrics   │  │  /metrics   │          │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │  │
│  │         │                │                │                    │  │
│  │         └────────────────┼────────────────┘                    │  │
│  │                          │                                      │  │
│  │                          ▼                                      │  │
│  │                 ┌─────────────────┐                            │  │
│  │                 │   PROMETHEUS    │◄──── Scrapes /metrics      │  │
│  │                 │    :9090        │       every 15 seconds     │  │
│  │                 └────────┬────────┘                            │  │
│  │                          │                                      │  │
│  └──────────────────────────┼──────────────────────────────────────┘  │
│                             │                                         │
│                             │ PromQL Queries                          │
│                             ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  METRICS-COLLECTOR (Python)                    │   │
│  │                                                                │   │
│  │  collectors/     → Fetches metrics from Prometheus            │   │
│  │  processors/     → Calculates aggregations                    │   │
│  │  graph_centrality/ → Computes service graph centralities      │   │
│  │  stress_index/   → Calculates pressure indices                │   │
│  │  exporters/      → Writes to dataset.csv                      │   │
│  │                                                                │   │
│  │  OUTPUT: dataset.csv (Training data for ML model)             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. Microservices expose metrics at `/metrics` endpoint
2. Prometheus scrapes these endpoints every 15-30 seconds
3. Metrics Collector queries Prometheus via PromQL
4. Collector processes and aggregates data
5. Output written to `dataset.csv` for ML training

---

## 2. Prerequisites Checklist

ආරම්භ කිරීමට පෙර මේවා ready කරගන්න:

- [ ] Docker Desktop installed & running
- [ ] Python 3.9+ installed
- [ ] `autoscaling-microservices-demo` project unzipped
- [ ] `METRICS-COLLECTOR` project ready
- [ ] Both projects in separate folders

**Folder Structure:**
```
your-workspace/
├── autoscaling-microservices-demo/    # Microservices
│   ├── services/
│   ├── infrastructure/
│   └── ...
│
└── METRICS-COLLECTOR/                  # Your collector
    ├── collectors/
    ├── config/
    ├── main.py
    └── ...
```

---

## 3. Step 1: Update Metrics Collector Settings

### 3.1 Update `config/settings.py`

ඔයාගේ METRICS-COLLECTOR folder එකේ `config/settings.py` file එක මේ විදියට update කරන්න:

```python
# config/settings.py
import os

# -------------------------------------------------------------------
# PROMETHEUS SETTINGS
# -------------------------------------------------------------------
# Docker Compose එකේ Prometheus port එක 9090
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# -------------------------------------------------------------------
# TARGET NAMESPACES IN YOUR CLUSTER
# -------------------------------------------------------------------
# Docker Compose වල namespace නැහැ, but for K8s later:
TARGET_NAMESPACES = [
    "autoscaling-demo",  # Kubernetes namespace
    "default"            # Fallback
]

# -------------------------------------------------------------------
# TARGET SERVICES TO COLLECT METRICS FROM
# -------------------------------------------------------------------
# *** IMPORTANT: මේ names microservices demo එකේ service names ***
TARGET_SERVICES = [
    "api-gateway",
    "user-service",
    "order-service",
    "inventory-service",
    "payment-service",
    "notification-service"
]

# -------------------------------------------------------------------
# CLUSTER INFO
# -------------------------------------------------------------------
CLUSTER_ID = os.getenv("CLUSTER_ID", "autoscaling-demo-local")

# -------------------------------------------------------------------
# OUTPUT DATASET
# -------------------------------------------------------------------
OUTPUT_DATASET_PATH = os.getenv("OUTPUT_DATASET_PATH", "output/dataset.csv")

# -------------------------------------------------------------------
# SCRAPE INTERVAL + WINDOW SIZE
# -------------------------------------------------------------------
# 30 seconds is good for testing, increase to 60-300 for production
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))

# -------------------------------------------------------------------
# TESTING OVERRIDES
# -------------------------------------------------------------------
QUEUE_TEST_MODE = os.getenv("QUEUE_TEST_MODE", "0") == "1"
ERROR_TEST_MODE = os.getenv("ERROR_TEST_MODE", "0") == "1"

# -------------------------------------------------------------------
# METRIC NAMES MAPPING (Match with microservices metrics)
# -------------------------------------------------------------------
# These should match the metric names exposed by microservices
METRIC_NAMES = {
    # HTTP metrics (from metrics-lib)
    "request_total": "http_requests_total",
    "request_duration": "http_request_duration_seconds",
    "request_rate": "request_rate_rps",
    "error_rate": "error_rate_percent",
    
    # Latency percentiles
    "latency_p50": "latency_p50_ms",
    "latency_p95": "latency_p95_ms", 
    "latency_p99": "latency_p99_ms",
    
    # Queue metrics
    "queue_length": "queue_length",
    
    # Service mesh metrics
    "inbound_request_rate": "inbound_request_rate_rps",
    "outbound_request_rate": "outbound_request_rate_rps",
    "mesh_latency_p95": "mesh_latency_p95_ms",
    
    # Graph centralities (calculated by collector)
    "degree_centrality": "degree_centrality",
    "betweenness_centrality": "betweenness_centrality",
    "closeness_centrality": "closeness_centrality",
    "eigenvector_centrality": "eigenvector_centrality",
    
    # Pressure indices
    "cpu_pressure": "cpu_pressure_index",
    "memory_pressure": "memory_pressure_index",
    "io_pressure": "io_pressure_index",
    "stress_index": "stress_index"
}
```

### 3.2 Update `config/constants.py`

```python
# config/constants.py
import os

# -------------------------------------------------------
# Sliding window + scrape interval
# -------------------------------------------------------
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))

# -------------------------------------------------------
# HTTP client retry behaviour
# -------------------------------------------------------
HTTP_RETRY_COUNT = int(os.getenv("HTTP_RETRY_COUNT", 3))
HTTP_RETRY_DELAY = float(os.getenv("HTTP_RETRY_DELAY", 1.0))

# -------------------------------------------------------
# Graph / centrality tuning
# -------------------------------------------------------
MIN_RPS_THRESHOLD = float(os.getenv("MIN_RPS_THRESHOLD", 0.001))  # Lower for testing

# Dataset version
DATASET_VERSION = "v1.0"

# -------------------------------------------------------
# Service Ports (for direct metric fetching if needed)
# -------------------------------------------------------
SERVICE_PORTS = {
    "api-gateway": 3000,
    "user-service": 3001,
    "order-service": 3002,
    "inventory-service": 3003,
    "payment-service": 3004,
    "notification-service": 3005
}
```

---

## 4. Step 2: Start Microservices Demo

### 4.1 Start with Docker Compose

```bash
# Navigate to microservices demo
cd autoscaling-microservices-demo/infrastructure/docker

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
sleep 30

# Verify all services are running
docker-compose ps
```

**Expected Output:**
```
NAME                    STATUS    PORTS
api-gateway             running   0.0.0.0:3000->3000/tcp
user-service            running   0.0.0.0:3001->3001/tcp
order-service           running   0.0.0.0:3002->3002/tcp
inventory-service       running   0.0.0.0:3003->3003/tcp
payment-service         running   0.0.0.0:3004->3004/tcp
notification-service    running   0.0.0.0:3005->3005/tcp
mongodb                 running   0.0.0.0:27017->27017/tcp
redis                   running   0.0.0.0:6379->6379/tcp
rabbitmq                running   0.0.0.0:5672->5672/tcp
kafka                   running   0.0.0.0:9092->9092/tcp
prometheus              running   0.0.0.0:9090->9090/tcp
grafana                 running   0.0.0.0:3001->3000/tcp
jaeger                  running   0.0.0.0:16686->16686/tcp
frontend                running   0.0.0.0:80->80/tcp
```

### 4.2 Check Service Health

```bash
# Test each service
curl http://localhost:3000/health  # API Gateway
curl http://localhost:3001/health  # User Service
curl http://localhost:3002/health  # Order Service
curl http://localhost:3003/health  # Inventory Service
curl http://localhost:3004/health  # Payment Service
curl http://localhost:3005/health  # Notification Service
```

---

## 5. Step 3: Verify Prometheus Metrics

### 5.1 Check Prometheus is Scraping

Open browser: **http://localhost:9090**

1. Go to "Status" → "Targets"
2. You should see all services listed as "UP"

### 5.2 Test PromQL Queries

In Prometheus UI, try these queries:

```promql
# Total HTTP requests
http_requests_total

# Request rate per service
request_rate_rps

# Error rate
error_rate_percent

# Latency P99
latency_p99_ms

# Queue length
queue_length

# All metrics from api-gateway
{job="api-gateway"}
```

### 5.3 Test Metrics Endpoints Directly

```bash
# Get raw metrics from each service
curl http://localhost:3000/metrics | head -50
curl http://localhost:3001/metrics | head -50
curl http://localhost:3002/metrics | head -50
```

**Expected Output (sample):**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/health",status="200"} 15
http_requests_total{method="GET",route="/api/users",status="200"} 3

# HELP request_rate_rps Current request rate per second
# TYPE request_rate_rps gauge
request_rate_rps{service="api-gateway"} 2.5

# HELP latency_p99_ms 99th percentile latency in ms
# TYPE latency_p99_ms gauge
latency_p99_ms{service="api-gateway"} 45.2
```

---

## 6. Step 4: Run Metrics Collector

### 6.1 Setup Python Environment

```bash
# Navigate to METRICS-COLLECTOR
cd METRICS-COLLECTOR

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**If requirements.txt doesn't exist, create it:**
```bash
cat > requirements.txt << 'EOF'
requests>=2.28.0
prometheus-client>=0.17.0
pandas>=2.0.0
numpy>=1.24.0
networkx>=3.0
pyyaml>=6.0
python-dotenv>=1.0.0
aiohttp>=3.8.0
EOF

pip install -r requirements.txt
```

### 6.2 Create Output Directory

```bash
mkdir -p output
```

### 6.3 Run the Collector

```bash
# Set environment variables (optional, defaults work)
export PROMETHEUS_URL="http://localhost:9090"
export OUTPUT_DATASET_PATH="output/dataset.csv"
export SCRAPE_INTERVAL_SECONDS=30

# Run main.py
python main.py
```

**Expected Output:**
```
[2024-01-15 10:30:00] INFO: Starting Metrics Collector
[2024-01-15 10:30:00] INFO: Prometheus URL: http://localhost:9090
[2024-01-15 10:30:00] INFO: Target Services: ['api-gateway', 'user-service', ...]
[2024-01-15 10:30:00] INFO: Scrape Interval: 30 seconds
[2024-01-15 10:30:00] INFO: Connecting to Prometheus...
[2024-01-15 10:30:01] INFO: Connected successfully
[2024-01-15 10:30:01] INFO: Starting collection loop...
[2024-01-15 10:30:01] INFO: Collecting metrics for api-gateway...
[2024-01-15 10:30:02] INFO: Collecting metrics for user-service...
...
[2024-01-15 10:30:05] INFO: Writing to output/dataset.csv
[2024-01-15 10:30:05] INFO: Collection cycle complete. Next in 30s...
```

---

## 7. Step 5: Generate Load for Training Data

Metrics collect වෙන්න නම් traffic එක ඕන. Load generate කරන්න:

### 7.1 Option A: Using Locust (Recommended)

```bash
# Install locust
pip install locust

# Navigate to load generator
cd autoscaling-microservices-demo/load-generator/locust

# Start Locust
locust -f locustfile.py --host=http://localhost:3000

# Open browser: http://localhost:8089
# Set: Users=50, Spawn Rate=5
# Click "Start Swarming"
```

### 7.2 Option B: Using curl in a Loop

```bash
# Simple load script
while true; do
    # Browse products (high traffic)
    curl -s http://localhost:3000/api/inventory/products > /dev/null &
    curl -s http://localhost:3000/api/inventory/products > /dev/null &
    curl -s http://localhost:3000/api/inventory/products > /dev/null &
    
    # User operations
    curl -s http://localhost:3000/api/users > /dev/null &
    
    # Health checks
    curl -s http://localhost:3000/health > /dev/null &
    curl -s http://localhost:3001/health > /dev/null &
    curl -s http://localhost:3002/health > /dev/null &
    
    sleep 0.5
done
```

### 7.3 Option C: Using Apache Bench (ab)

```bash
# Install ab (comes with Apache)
# Ubuntu: sudo apt install apache2-utils
# macOS: already installed

# Run load test
ab -n 1000 -c 10 http://localhost:3000/api/inventory/products
ab -n 500 -c 5 http://localhost:3000/api/users
```

### 7.4 Create Various Traffic Patterns

ML model එකට diverse data ඕන. Different patterns generate කරන්න:

```bash
# Pattern 1: Normal traffic (5 minutes)
locust --host=http://localhost:3000 --users=20 --spawn-rate=2 --run-time=5m --headless

# Pattern 2: High traffic spike (2 minutes)
locust --host=http://localhost:3000 --users=100 --spawn-rate=20 --run-time=2m --headless

# Pattern 3: Low traffic (5 minutes)
locust --host=http://localhost:3000 --users=5 --spawn-rate=1 --run-time=5m --headless

# Pattern 4: Gradual increase (10 minutes)
locust --host=http://localhost:3000 --users=50 --spawn-rate=1 --run-time=10m --headless
```

---

## 8. Step 6: Verify Collected Data

### 8.1 Check Output File

```bash
# View first few rows
head -20 output/dataset.csv

# Count rows
wc -l output/dataset.csv

# Check columns
head -1 output/dataset.csv | tr ',' '\n' | nl
```

### 8.2 Expected CSV Columns

```
timestamp,service_name,cluster_id,
node_cpu_percent,node_memory_percent,node_disk_io_percent,node_network_rx_bytes,node_network_tx_bytes,
pod_cpu_avg_percent,pod_cpu_p95_percent,pod_memory_avg_percent,pod_memory_p95_percent,pod_restart_count,
request_rate_rps,latency_p50_ms,latency_p95_ms,latency_p99_ms,error_rate_4xx_percent,error_rate_5xx_percent,queue_length,application_saturation,
inbound_request_rate_rps,outbound_request_rate_rps,mesh_latency_p95_ms,retry_rate_percent,active_connections,
degree_centrality,betweenness_centrality,closeness_centrality,eigenvector_centrality,
cpu_pressure_index,memory_pressure_index,io_pressure_index,stress_index,
current_replicas,recommended_replicas
```

### 8.3 Validate Data Quality

```python
# Quick validation script
import pandas as pd

df = pd.read_csv('output/dataset.csv')
print(f"Total rows: {len(df)}")
print(f"Services: {df['service_name'].unique()}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"\nColumn stats:")
print(df.describe())
print(f"\nNull values:")
print(df.isnull().sum())
```

---

## 9. Kubernetes Deployment

Docker Compose වලින් test කලාට පස්සේ, production-like environment එකකට යන්න:

### 9.1 Update Prometheus ConfigMap

```yaml
# infrastructure/kubernetes/monitoring/prometheus-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: autoscaling-demo
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
      - job_name: 'api-gateway'
        static_configs:
          - targets: ['api-gateway:3000']
        metrics_path: /metrics
      
      - job_name: 'user-service'
        static_configs:
          - targets: ['user-service:3001']
        metrics_path: /metrics
      
      - job_name: 'order-service'
        static_configs:
          - targets: ['order-service:3002']
        metrics_path: /metrics
      
      - job_name: 'inventory-service'
        static_configs:
          - targets: ['inventory-service:3003']
        metrics_path: /metrics
      
      - job_name: 'payment-service'
        static_configs:
          - targets: ['payment-service:3004']
        metrics_path: /metrics
      
      - job_name: 'notification-service'
        static_configs:
          - targets: ['notification-service:3005']
        metrics_path: /metrics
      
      # Kubernetes service discovery (alternative)
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['autoscaling-demo']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
```

### 9.2 Deploy Metrics Collector to K8s

```yaml
# infrastructure/kubernetes/monitoring/metrics-collector.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metrics-collector
  namespace: autoscaling-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: metrics-collector
  template:
    metadata:
      labels:
        app: metrics-collector
    spec:
      containers:
      - name: metrics-collector
        image: your-registry/metrics-collector:latest
        env:
        - name: PROMETHEUS_URL
          value: "http://prometheus:9090"
        - name: SCRAPE_INTERVAL_SECONDS
          value: "30"
        - name: OUTPUT_DATASET_PATH
          value: "/data/dataset.csv"
        volumeMounts:
        - name: data
          mountPath: /data
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: metrics-data-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: metrics-data-pvc
  namespace: autoscaling-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 9.3 Create Dockerfile for Metrics Collector

```dockerfile
# METRICS-COLLECTOR/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

CMD ["python", "main.py"]
```

### 9.4 Build and Deploy

```bash
# Build image
cd METRICS-COLLECTOR
docker build -t your-registry/metrics-collector:latest .
docker push your-registry/metrics-collector:latest

# Deploy
kubectl apply -f infrastructure/kubernetes/monitoring/metrics-collector.yaml

# Check logs
kubectl logs -f deployment/metrics-collector -n autoscaling-demo
```

---

## 10. Troubleshooting

### 10.1 Prometheus Cannot Reach Services

**Problem:** Targets show as "DOWN" in Prometheus

**Solution:**
```bash
# Check service is running
docker-compose ps

# Check network
docker network ls
docker network inspect docker_app-network

# Test from Prometheus container
docker exec -it prometheus wget -qO- http://api-gateway:3000/metrics
```

### 10.2 No Metrics Data

**Problem:** CSV file is empty or has nulls

**Solution:**
```bash
# 1. Verify metrics exist in Prometheus
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# 2. Check if services are exposing metrics
curl http://localhost:3000/metrics

# 3. Generate some traffic first
curl http://localhost:3000/api/users
curl http://localhost:3000/api/inventory/products
```

### 10.3 Connection Refused to Prometheus

**Problem:** `ConnectionRefusedError: [Errno 111]`

**Solution:**
```bash
# Check Prometheus is running
docker-compose ps prometheus

# Check port binding
netstat -tlnp | grep 9090

# Try different URL
export PROMETHEUS_URL="http://127.0.0.1:9090"
# or
export PROMETHEUS_URL="http://host.docker.internal:9090"  # If collector in Docker
```

### 10.4 Graph Centrality All Zeros

**Problem:** Centrality metrics are 0.0

**Solution:**
```bash
# Need inter-service traffic to build graph
# Make requests that trigger service-to-service calls:

# This calls: api-gateway → order-service → inventory-service
curl -X POST http://localhost:3000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"productId":"test","quantity":1}]}'

# Wait for graph to build (few minutes of traffic)
```

### 10.5 Python Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure you're in venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

---

## 📊 Quick Reference: Metric Mappings

| ML Training Column | Prometheus Metric | Source |
|-------------------|-------------------|--------|
| request_rate_rps | request_rate_rps | metrics-lib |
| latency_p50_ms | latency_p50_ms | metrics-lib |
| latency_p95_ms | latency_p95_ms | metrics-lib |
| latency_p99_ms | latency_p99_ms | metrics-lib |
| error_rate_4xx | error_rate_4xx_percent | metrics-lib |
| error_rate_5xx | error_rate_5xx_percent | metrics-lib |
| queue_length | queue_length | metrics-lib |
| inbound_request_rate | inbound_request_rate_rps | httpMetrics |
| outbound_request_rate | outbound_request_rate_rps | httpMetrics |
| mesh_latency_p95 | mesh_latency_p95_ms | httpMetrics |
| degree_centrality | (calculated) | graph_centrality |
| betweenness_centrality | (calculated) | graph_centrality |
| closeness_centrality | (calculated) | graph_centrality |
| eigenvector_centrality | (calculated) | graph_centrality |
| cpu_pressure_index | (calculated) | stress_index |
| memory_pressure_index | (calculated) | stress_index |
| stress_index | (calculated) | stress_index |

---

## ✅ Integration Checklist

- [ ] METRICS-COLLECTOR settings.py updated with correct service names
- [ ] Docker Compose started and all services healthy
- [ ] Prometheus UI accessible at http://localhost:9090
- [ ] All services showing as "UP" in Prometheus targets
- [ ] Metrics visible in Prometheus queries
- [ ] Python venv created and dependencies installed
- [ ] Metrics Collector running without errors
- [ ] Load generator producing traffic
- [ ] dataset.csv being populated
- [ ] All columns have non-null values
- [ ] Graph centralities showing non-zero values

---

**🎉 ඔයා දැන් ready ML training data collect කරන්න!**

Questions? Check the ERRORS.md in your METRICS-COLLECTOR project.
