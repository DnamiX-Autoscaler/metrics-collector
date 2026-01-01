# Explanation of Graph Centrality Metrics (With Simple Examples)

## Introduction

In this research, Kubernetes microservices are modeled as a **graph** to understand not only resource usage, but also **service importance, traffic flow, and failure impact**.

- **Nodes** represent services
- **Edges** represent service-to-service calls
- **Direction** represents request flow
- **Edge weight** represents traffic intensity (RPS)

Using this graph, **four centrality metrics** are computed to extract **structural intelligence** that cannot be captured by CPU or memory metrics alone.

---

## Why Graph Centrality?

Traditional auto-scaling decisions are based on:
- CPU usage
- Memory usage

However, these metrics **ignore service dependencies**.

Graph centrality answers questions such as:
- Which service is most depended upon?
- Which service is a traffic bottleneck?
- Which service failure will affect the whole system?

---

## Example Service Graph (Simple)

Consider a system with the following services:

Frontend → Order → Payment
Frontend → Product → Inventory

Frontend -> Product -> Inventory
|       
v       
Order
|
v
Payment 


---

## 1. Degree Centrality

### What It Means (Simple)

Degree centrality measures:
> **How many direct connections a service has**

### Algorithm Logic

- Count how many neighbors a node has
- Normalize the value between 0 and 1
- Direction is ignored (converted to undirected)

### Example

| Service   | Connections | Degree Centrality |
|----------|-------------|------------------|
| Frontend | 2           | High             |
| Order    | 2           | Medium           |
| Payment  | 1           | Low              |

### Interpretation

- **Frontend** has high degree centrality
- Many services depend on it directly

### Why This Matters for Scaling

If a high-degree service becomes slow:
- Multiple downstream services are affected
- Scaling it early prevents system-wide slowdown

---

## 2. Betweenness Centrality

### What It Means (Simple)

Betweenness centrality measures:
> **How often a service lies on the critical path between other services**

### Algorithm Logic

- Compute all shortest paths in the graph
- Count how many pass through each node
- Normalize the result

### Example

In the path:

Frontend → Order → Payment


The **Order** service lies in the middle.

| Service | Betweenness |
|-------|-------------|
| Order | High        |
| Frontend | Low     |
| Payment | Low      |

### Interpretation

- **Order** is a traffic bridge
- If it fails, requests cannot reach Payment

### Why This Matters for Scaling

Even if Order has low CPU:
- It must be scaled because it is a **traffic bottleneck**
- Prevents cascading failures

---

## 3. Closeness Centrality

### What It Means (Simple)

Closeness centrality measures:
> **How quickly a service can reach all other services**

### Algorithm Logic

- Compute shortest distance from one service to all others
- Take the inverse of the total distance

### Example

| Service   | Average Distance to Others | Closeness |
|----------|----------------------------|-----------|
| Frontend | Low                        | High      |
| Inventory| High                       | Low       |

### Interpretation

- **Frontend** can reach all services quickly
- It is latency-sensitive

### Why This Matters for Scaling

If a high-closeness service becomes slow:
- End-to-end latency increases quickly
- Scaling reduces overall response time

---

## 4. Eigenvector Centrality

### What It Means (Simple)

Eigenvector centrality measures:
> **How important a service is based on the importance of the services it connects to**

### Algorithm Logic

- A service is important if it connects to other important services
- Influence spreads through the network

### Example

If:
- Frontend is very important
- Order connects to Frontend

Then:
- Order also becomes important

| Service | Eigenvector |
|-------|-------------|
| Frontend | Very High |
| Order | High |
| Payment | Medium |

### Interpretation

- High eigenvector services affect **the whole system**
- Failures propagate widely

### Why This Matters for Scaling

Scaling these services:
- Improves system-wide stability
- Prevents large-scale outages

---

## Summary Table

| Metric | Answers Which Question? | Scaling Benefit |
|------|-------------------------|----------------|
| Degree | How connected is the service? | Prevents overload hotspots |
| Betweenness | Is it a traffic bottleneck? | Prevents cascading failures |
| Closeness | How fast does impact spread? | Reduces latency spikes |
| Eigenvector | How globally important is it? | Improves system resilience |

---

## Why This Approach Is Suitable for Research

- Uses standard graph theory algorithms
- Uses real runtime telemetry (Istio)
- Captures dependency-aware intelligence
- Produces ML-ready numerical features
- Goes beyond resource-only scaling

---

## Key Message for Research Panel

> "Instead of scaling based only on CPU or memory, this system understands how services interact.  
> Graph centrality metrics allow the system to identify important, sensitive, and risky services and make smarter scaling decisions."

---



