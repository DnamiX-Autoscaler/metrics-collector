
venv\Scripts\activate 

$env:TARGET_NAMESPACES="ecommerce-test"
python main.py

node_cpu_seconds_total

kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

for ($i=1; $i -le 5555555555; $i++) { curl http://localhost:3001/metrics }