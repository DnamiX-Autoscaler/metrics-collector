# Graph Centrality Metrics – Mathematical Example (Step-by-Step)

## Objective

This section explains **how graph centrality values are mathematically derived** using a **simple microservice dependency graph**, so that the research panel can clearly understand **how final numerical values are obtained and justified**.

---

## Example Service Call Graph

Assume a microservice system with **four services**:

- **A** – Frontend  
- **B** – Order  
- **C** – Payment  
- **D** – Inventory  

### Service Call Relationships (Directed)

- A → B  
- A → C  
- B → C  
- C → D  

### Directed Graph Representation

A ──▶ B ──▶ C ──▶ D
│           ▲
└──────────▶┘


---

## Step 1: Graph Definition

- Nodes: {A, B, C, D}  
- Total nodes (N) = 4  
- Directed, unweighted graph  
- Centrality metrics are used as **structural features for ML-based auto-scaling decisions**

---

## 1️⃣ Degree Centrality (Undirected – Structural Connectivity)

### Definition

Degree Centrality measures **how many direct connections a node has**.

DC(v) = degree(v) / (N - 1)


### Conversion to Undirected Graph

To capture **structural dependency strength**, the graph is treated as undirected.

Edges become:

- A—B  
- A—C  
- B—C  
- C—D  

### Degree Count

| Node | Degree |
|------|--------|
| A    | 2      |
| B    | 2      |
| C    | 3      |
| D    | 1      |

### Degree Centrality Values  
(N − 1 = 3)

| Node | Calculation | DC   |
|------|-------------|------|
| A    | 2 / 3       | 0.67 |
| B    | 2 / 3       | 0.67 |
| C    | 3 / 3       | 1.00 |
| D    | 1 / 3       | 0.33 |

### Interpretation

- **C (Payment)** has the highest local connectivity.
- Many services directly depend on it.

---

## 2️⃣ Betweenness Centrality (Directed – Traffic Mediation)

### Definition

Betweenness Centrality measures **how frequently a node lies on the shortest paths between other nodes**.

BC(v) = Σ (σ_st(v) / σ_st)


Where:

- σ_st = total shortest paths from s to t  
- σ_st(v) = shortest paths passing through v  

---

### All Shortest Paths (Directed)

| Source → Target | Shortest Path |
|-----------------|---------------|
| A → B           | A → B         |
| A → C           | A → C         |
| A → D           | A → C → D     |
| B → C           | B → C         |
| B → D           | B → C → D     |

Total shortest paths = **6**

---

### Node Participation (Middle Nodes Only)

| Node | Paths Passing Through |
|------|-----------------------|
| A    | None                  |
| B    | None                  |
| C    | A → D, B → D          |
| D    | None                  |

---

### Normalized Betweenness Centrality

| Node | BC   |
|------|------|
| A    | 0.00 |
| B    | 0.00 |
| C    | 0.33 |
| D    | 0.00 |

### Interpretation

- **C** is a traffic bottleneck.
- Many requests must pass through it to reach D.

---

## 3️⃣ Closeness Centrality (Directed – Latency Reachability)

### Definition

Closeness Centrality measures **how close a node is to all other reachable nodes**.

CC(v) = (N - 1) / Σ d(v, u)


---

### Shortest Distances

| From | Reachable Nodes        | Distance Sum |
|------|------------------------|--------------|
| A    | B(1), C(1), D(2)       | 4            |
| B    | C(1), D(2)             | 3            |
| C    | D(1)                   | 1            |
| D    | —                      | ∞            |

---

### Closeness Centrality Values  
(N − 1 = 3)

| Node | Calculation | CC   |
|------|-------------|------|
| A    | 3 / 4       | 0.75 |
| B    | 3 / 3       | 1.00 |
| C    | 3 / 1       | 3.00 |
| D    | 0           | 0.00 |

### Interpretation

- **C** is closest to downstream services.
- High impact on latency propagation.

---

## 4️⃣ Eigenvector Centrality (Undirected – Global Influence)

### Definition

Eigenvector Centrality measures **global influence**.

A node is important if it connects to **other important nodes**.

A x = λ x


---

### Adjacency Matrix (Undirected)

    A B C D
A [ 0 1 1 0 ]
B [ 1 0 1 0 ]
C [ 1 1 0 1 ]
D [ 0 0 1 0 ]


---

### Eigenvector Centrality (Normalized – L2)

| Node | EC   |
|------|------|
| A    | 0.52 |
| B    | 0.52 |
| C    | 0.61 |
| D    | 0.28 |

### Interpretation

- **C** has the highest global influence.
- Failure at C affects the entire system.

---

## Final Centrality Feature Vector (ML-Ready)

```json
{
  "A": {
    "degree": 0.67,
    "betweenness": 0.00,
    "closeness": 0.75,
    "eigenvector": 0.52
  },
  "B": {
    "degree": 0.67,
    "betweenness": 0.00,
    "closeness": 1.00,
    "eigenvector": 0.52
  },
  "C": {
    "degree": 1.00,
    "betweenness": 0.33,
    "closeness": 3.00,
    "eigenvector": 0.61
  },
  "D": {
    "degree": 0.33,
    "betweenness": 0.00,
    "closeness": 0.00,
    "eigenvector": 0.28
  }
}
