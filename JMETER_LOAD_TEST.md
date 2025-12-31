store-front → order-service / product-service internally call
Istio + pod metrics generate

🟢 STEP 1: JMeter install & start
1️⃣ Java check
java -version

2️⃣ JMeter open
cd C:\tools\apache-jmeter-5.6.3\bin
.\jmeter.bat

🟢 STEP 2: New Test Plan
JMeter open → Test Plan
Rename → Store Load Test

🟢 STEP 3: Thread Group (users)
Right click Test Plan →
Add → Threads (Users) → Thread Group
Set:
Number of Threads (Users): 25
Ramp-up period: 10
Loop Count: Forever
👉 Meaning: 25 users gradually start within 10 seconds.

🟢 STEP 4: HTTP Request Defaults (Base URL)
Thread Group → Right click →
Add → Config Element → HTTP Request Defaults
Fill:
Protocol: http
Server Name or IP: localhost
Port Number: 32325 ← store-front

🟢 STEP 5: HTTP Header Manager (JSON support)
Thread Group → Right click →
Add → Config Element → HTTP Header Manager
Add:
Content-Type : application/json

🟢 STEP 6: Add Load Requests (VERY IMPORTANT)
🔹 Request 1: Store Front Home (GET)
Thread Group →
Add → Sampler → HTTP Request
Name: GET Store Front
Method: GET
Path: /

🔹 Request 2: Product List (GET)
(Assume store-front has /products)
Name: GET Products
Method: GET
Path: /products

🔹 Request 3: Place Order (POST)
(Assume /api/orders exposed via store-front)
Name: POST Order
Method: POST
Path: /api/orders
Body Data:
{
  "customerId": "load-test",
  "items": [
    { "productId": "p1", "qty": 1 }
  ]
}
📌 If your real path is different, change only Path field.

🟢 STEP 7: Add Listeners (see results)
Thread Group → Right click →
Add → Listener → Summary Report
(Optional debugging)
View Results Tree

🟢 STEP 8: Start Load Test
▶️ Click Start
👉 Now JMeter is hammering store-front.

🧪 STEP 9: Confirm metrics in Prometheus
1️⃣ Open Prometheus
kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
Browser: http://localhost:9090

2️⃣ Run these queries
🔹 Istio request rate
# um(rate(istio_requests_total[1m]))

🔹 Store-front traffic
# sum(rate(istio_requests_total{destination_service_name=~" *store-front.*"}[1m]))

🔹 Order service traffic
# sum(rate(istio_requests_total{destination_service_name=~".*order-service.*"}[1m]))

🔹 Pod CPU
# sum(rate(container_cpu_usage_seconds_total{pod!=""}[1m])) * 100

🔹 Pod Memory
# sum(container_memory_usage_bytes{pod!=""}) / (1024*1024)

🟢 STEP 10: Metrics-Collector fetch
One-time fetch
Browser: 
http://localhost:8000/metrics/live
Real-time stream (SSE)
http://localhost:8000/metrics/live-stream

PowerShell:
curl http://localhost:8000/metrics/live-stream
👉 Now you should see:
pod_cpu_usage_percent_p95 > 0
pod_memory_usage_mb_p95 > 0
current_pod_count > 0
stress_index > 0



