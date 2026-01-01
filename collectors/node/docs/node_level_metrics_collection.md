# Node-Level Metrics Collection Using Node Exporter

## Purpose of Node-Level Metrics

Node-level metrics represent the **physical and operating-system–level resource behavior** of a Kubernetes cluster node.  
Unlike pod-level metrics, node metrics capture **infrastructure saturation**, which directly affects pod performance and auto-scaling decisions.

In this research, Node Exporter and cAdvisor metrics are used to collect:
- CPU utilization
- Memory usage
- Disk I/O activity
- Network I/O activity

These metrics are aggregated into a **single, unified node-level feature vector** for ML-ready datasets.

---

## Data Sources

The node-level metrics are collected from Prometheus using:

| Component | Metrics Source |
|--------|---------------|
| CPU | cAdvisor (`container_cpu_usage_seconds_total`) |
| Memory | Node Exporter (`node_memory_*`) |
| Disk | Node Exporter (`node_disk_*`) |
| Network | Node Exporter (`node_network_*`) |

All metrics are queried through the **Prometheus HTTP API**.

---

## Overall Collection Architecture

1. Individual collectors retrieve raw metrics from Prometheus
2. Metrics are grouped by Prometheus `instance`
3. Multiple interfaces/devices are **merged**
4. Metrics are normalized into a **single node identity**
5. Final output is a **node-level ML-ready structure**

---

## Node Metrics Aggregation Logic

### Aggregator Responsibility

The `node_aggregator.py` acts as the **single integration point** that:
- Calls all node metric collectors
- Merges per-instance metrics
- Produces one consolidated node record

### Aggregation Algorithm

```text
For each metric type:
    For each Prometheus instance:
        Sum all values
Assign merged values to detected node name
