# Pod-Level Metrics Collection Using cAdvisor

## Purpose of Pod-Level Metrics

Pod-level metrics represent the **runtime behavior of application workloads** inside Kubernetes.  
Unlike node-level metrics, pod metrics directly reflect **application stress, scaling pressure, and failure signals**.

In this research, cAdvisor and Kubernetes metrics are used to collect:
- Pod CPU usage (average & p95)
- Pod memory usage (average & p95)
- Pod restart count
- Pod resource limits (CPU & memory)
- Current pod count per namespace

These metrics are aggregated into a **single ML-ready feature vector per pod**.

---

## Data Sources

| Metric Type | Source |
|-----------|--------|
| CPU usage | cAdvisor (`container_cpu_usage_seconds_total`) |
| Memory usage | cAdvisor (`container_memory_usage_bytes`) |
| Restart count | kube-state-metrics |
| Resource limits | kube-state-metrics |

Metrics are queried using the **Prometheus HTTP API**.

---

## Overall Collection Architecture

1. Collect raw pod metrics from Prometheus
2. Group metrics by `pod` label
3. Aggregate multiple containers per pod
4. Compute statistical summaries (avg, p95)
5. Merge metrics into a unified pod record

---

## Pod Metrics Aggregation Logic

The `pod_aggregator.py` module:
- Calls all individual collectors
- Merges metrics per pod
- Ensures consistent schema
- Adds namespace-level pod count

This ensures **each pod has a complete, self-contained metric vector**.

---

## Pod CPU Usage Collection

### Metric Used

