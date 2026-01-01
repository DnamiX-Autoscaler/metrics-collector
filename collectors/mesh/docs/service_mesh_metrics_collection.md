# Service-Level Metrics Collection Using Istio Service Mesh

## Purpose of Service Mesh Metrics

Service-mesh–level metrics capture **inter-service communication behavior** that cannot be observed using only pod-level or application-level metrics.

While:
- Pod metrics show *how a service uses resources*
- Application metrics show *how a service responds to requests*

Service mesh metrics show:
- **How traffic flows between services**
- **How the network behaves**
- **How failures propagate across services**

In this research, Istio telemetry is used to collect **service-level communication metrics**, enabling topology-aware and reliability-aware auto-scaling.

---

## Data Source: Istio Telemetry

Istio automatically emits detailed metrics via Envoy sidecars, including:

- `istio_requests_total`
- `istio_request_duration_milliseconds_bucket`
- `istio_tcp_connections_*`
- `istio_authentication_handshake_errors_total`

These metrics are scraped by Prometheus and queried using the Prometheus HTTP API.

---

## Overall Collection Architecture

1. Each service communicates via Istio sidecars
2. Envoy proxies emit traffic and latency metrics
3. Prometheus scrapes Istio metrics
4. The mesh collector queries metrics per service
5. Multiple label variations are tried for robustness
6. Metrics are merged into a unified service-level feature vector

The `mesh_aggregator.py` module orchestrates the entire process.

---

## Service Name Mapping Logic

### Problem

Istio metrics may expose service identifiers in different forms:
- `order-service`
- `order_service`
- `order`

If the label does not match exactly, metrics may appear as missing.

---

### Solution: Candidate Label Mapping

The system generates multiple candidate labels using:

```text
order-service → order_service → order
