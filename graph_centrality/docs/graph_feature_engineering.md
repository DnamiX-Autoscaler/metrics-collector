# Graph-Based Feature Engineering Using Centrality Metrics

## Overview

This module implements **graph-based feature engineering** to transform raw Kubernetes service-mesh telemetry into **ML-ready structural features**.  
Instead of relying only on traditional resource metrics (CPU, memory), the system models **runtime service dependencies as a graph** and extracts **graph-theoretic centrality measures** to capture service importance, traffic influence, and failure propagation potential.

This approach enables **topology-aware auto-scaling intelligence**, which is not supported by conventional threshold-based scaling systems.

---

## Motivation

Traditional Kubernetes auto-scaling approaches (e.g., HPA) are:
- Resource-centric (CPU / memory only)
- Blind to service-to-service dependencies
- Unable to detect traffic bottlenecks or cascading failures

However, modern microservice systems exhibit **complex runtime interactions**, especially when deployed with a service mesh such as Istio.

To address this, we:
1. Represent service interactions as a **directed graph**
2. Apply **graph centrality algorithms**
3. Convert structural properties into **numerical ML features**

---

## Service Dependency Graph Construction

### Graph Definition

- **Nodes**: Kubernetes services (Istio workloads)
- **Edges**: Directed service-to-service calls
- **Edge Weight**: Request rate (RPS)

### Data Source

Istio Telemetry v2 metric:


# Graph Construction Logic

Directed weighted graph
Nodes = services
Edges = service calls
Weight = RPS

G = nx.DiGraph()

for src, dst, rps in edges:
    if G.has_edge(src, dst):
        G[src][dst]["weight"] += rps
    else:
        G.add_edge(src, dst, weight=rps)

## Degree Centrality

**Algorithm Logic**

Degree centrality = local connectivity
Undirected graph → total neighborhood importance

UG = G.to_undirected()
dc = nx.degree_centrality(UG)

## Betweenness Centrality

**Algorithm Logic**

Identifies traffic bottlenecks
Shortest-path based
Normalized

bc = nx.betweenness_centrality(
    G,
    normalized=True,
    weight=None
)

## Closeness Centrality

**Algorithm Logic**

Measures reachability speed
Directed call g*raph
Unweighted paths

cc = nx.closeness_centrality(G)

## Eigenvector Centrality

**Algorithm Logic**

Measures indirect global influence
Needs numerical stability

UG = G.to_undirected()
ec = nx.eigenvector_centrality_numpy(UG)

------------------------------------------

### Feature Aggregation

**Theory**

Merge all centralities per service
Missing values → zero

result[svc] = {
    "degree_centrality": degree.get(svc, 0.0),
    "betweenness_centrality": between.get(svc, 0.0),
    "closeness_centrality": close.get(svc, 0.0),
    "eigenvector_centrality": eigen.get(svc, 0.0),
}

