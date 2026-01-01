# Application-Level Metrics Collection Using Prometheus Client Library

## Purpose of Application-Level Metrics

Application-level metrics represent the **end-user–visible behavior** of a microservice.  
While node- and pod-level metrics show infrastructure and runtime stress, application-level metrics capture **service performance, reliability, and saturation**, which are critical for intelligent auto-scaling decisions.

In this research, application-level metrics are collected using:
- Custom application instrumentation (Prometheus client library)
- Standard HTTP metrics exposed by services
- Prometheus HTTP API queries

The collected metrics describe **how well a service is serving traffic**, not just how much resource it consumes.

---

## Data Sources

Application metrics are exposed by services using a **Prometheus client library** (e.g., for Node.js, Python, Java).

The following metric families are used:

| Metric Category | Source |
|---------------|--------|
| Request rate (RPS) | `http_requests_total` |
| Error rates | `http_requests_total` (status labels) |
| Latency | `http_request_duration_milliseconds_bucket` |
| Queue length | `app_queue_length` (custom metric) |

---

## Overall Collection Architecture

1. Each application exposes `/metrics` endpoint
2. Prometheus scrapes metrics at regular intervals
3. Metrics are queried using time-windowed PromQL
4. Service-level statistics are computed
5. Metrics are merged into a unified application feature vector

The `app_aggregator.py` module orchestrates this entire process.

---

## Service Name Resolution Logic

### Problem

Different systems may expose service names differently:
- `order-service`
- `order_service`
- `order`

### Solution

The aggregator attempts multiple candidate labels:

```text
order-service → order_service → order
