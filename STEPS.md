# SETUP

## Python install
python --version 

## Virtual environment create
python -m venv venv 

## Virtual env activate
venv\Scripts\activate 

## Install relvent libraries
pip install requests networkx boto3 pytest matplotlib 

# SOMETIME AN ERROR IS OCCUR LETS FIX IT

## pip upgrade
python -m pip install --upgrade pip 

## Correct way to install ALL required librarie
pip install requests networkx boto3 pytest matplotlib python-dateutil

## Confirm the installation
pip list 

# RUN # -------------------------------------------------

## Virtual env activate
venv\Scripts\activate 

## Pipeline run
python main.py 

## One File Run
python collectors/node/node_cpu_collector.py


# DATASET VERIFY

## CSV file
output/dataset/metrics_dataset.csv 

## JSON lines file
output/dataset/metrics_dataset.jsonl 

## Raw Prometheus dumps
output/raw/ 

# RUN

## All tests folder run
pytest -q

### RUN PROMETHEUS
kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

### GET ALL PODS
kubectl get pods -o wide

### GET ALL SERVICES
kubectl get svc -n default

### DEPLOYED YAML
kubectl apply -f src/store-admin/service.yaml

### RESTART DEPLOYMENT
kubectl rollout restart deploy store-front

### DELETE DEPLOYMENT
kubectl delete -f mesh-metrics-test.yaml
kubectl delete -f tests/istio/mesh-traffic-generator.yaml

### TRAFIC GENERATOR
kubectl get pods -n default | findstr mesh-traffic-generator

# RUN TESTS

## Run with injection
$env:QUEUE_TEST_MODE="1"
python main.py
------------------
$env:ERROR_TEST_MODE="1"
$env:QUEUE_TEST_MODE="1"
python main.py
------------------
$env:WINDOW_SIZE_SECONDS="60"
$env:SCRAPE_INTERVAL_SECONDS="99999"
python main.py











