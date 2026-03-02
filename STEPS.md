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

$env:TARGET_NAMESPACES="ecommerce-test"
python main.py

$env:TARGET_NAMESPACES="default,ecommerce-test,monitoring,istio-system"
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

# TEST RUN

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

while ($true) {
  Invoke-WebRequest -Uri http://localhost:30080/" -UseBasicParsing | Out-Null
  Start-Sleep -Milliseconds 200
}

kubectl exec -it mesh-traffic-generator-6b8745d9f8-8pnsf -n default -- sh

kubectl run traffic-gen --image=busybox -n default --restart=Never -- sh -c "while true; do wget -qO- http://product-service.default.svc.cluster.local:3000 > /dev/null; sleep 0.2; done"


## SWITCH LOCAL AND PROD
kubectl config use-context docker-desktop
kubectl config use-context sr-research-aks

### VERIFY IT
kubectl config current-context

# API
## RUN UVICORN
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
python -m uvicorn api.server:app --reload

# ENDPOINTS
http://localhost:8000/metrics/live
http://localhost:8000/metrics/live-stream

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


# Clean cluster 

kubectl delete namespace monitoring
kubectl delete namespace ecommerce-prod

docker image prune -a
docker volume prune

wsl --shutdown





