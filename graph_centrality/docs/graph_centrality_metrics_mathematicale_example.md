# Graph Centrality Metrics – Mathematical Example (Step-by-Step)

## Objective

This section explains **how graph centrality values are mathematically derived**, using a **simple service graph**, so that the research panel can clearly understand **how final numerical values are obtained**.

---

## Example Service Call Graph

Assume a microservice system with **4 services**:

- A = Frontend  
- B = Order  
- C = Payment  
- D = Inventory  

### Service Call Relationships

A → B
A → C
B → C
C → D

### Directed Graph Representation

A ──▶ B ──▶ C ──▶ D
│           ▲
└──────────▶┘


---

## Step 1: Graph Definition

- Nodes: {A, B, C, D}
- Total nodes (N) = 4
- Directed, unweighted graph (for centrality stability)

---

## 1️⃣ Degree Centrality (Undirected)

### Definition

Degree Centrality measures **how many direct connections a node has**.

Formula:

Degree Centrality(v) = degree(v) / (N - 1)

### Convert to Undirected Graph

Edges become:
A—B, A—C, B—C, C—D


### Degree Count

| Node | Degree |
|----|-------|
| A | 2 |
| B | 2 |
| C | 3 |
| D | 1 |

### Final Degree Centrality Values

(N − 1 = 3)

| Node | Calculation | Value |
|----|------------|-------|
| A | 2 / 3 | **0.67** |
| B | 2 / 3 | **0.67** |
| C | 3 / 3 | **1.00** |
| D | 1 / 3 | **0.33** |

### Interpretation

- **C (Payment)** has the highest local dependency.
- Many services directly depend on it.

---

## 2️⃣ Betweenness Centrality (Directed)

### Definition

Betweenness Centrality measures **how often a node lies on shortest paths between other nodes**.

Formula:

CB(v) = Σ (σst(v) / σst)


Where:
- σst = total shortest paths from s to t
- σst(v) = shortest paths passing through v

---

### Step: All Shortest Paths

| Path | Shortest Path |
|----|--------------|
| A → B | A→B |
| A → C | A→C |
| A → D | A→C→D |
| B → C | B→C |
| B → D | B→C→D |

---

### Node Participation in Paths

| Node | Paths Passing Through |
|----|-----------------------|
| A | None |
| B | A→B |
| C | A→D, B→D |
| D | None |

---

### Raw Betweenness Scores

- Total node pairs excluding self = 6
- Normalize automatically (NetworkX standard)

| Node | Relative Betweenness |
|----|----------------------|
| A | 0.00 |
| B | 0.17 |
| C | **0.33** |
| D | 0.00 |

### Interpretation

- **C** is a traffic bottleneck.
- Many requests must pass through it to reach D.

---

## 3️⃣ Closeness Centrality (Directed)

### Definition

Closeness Centrality measures **how close a node is to all others**.

Formula:

CC(v) = 1 / Σ distance(v, u)


---

### Shortest Distances

| From | To Others | Sum |
|----|----------|-----|
| A | B(1), C(1), D(2) | 4 |
| B | C(1), D(2) | 3 |
| C | D(1) | 1 |
| D | — | ∞ |

---

### Closeness Values

| Node | Calculation | Value |
|----|------------|-------|
| A | 1 / 4 | **0.25** |
| B | 1 / 3 | **0.33** |
| C | 1 / 1 | **1.00** |
| D | 0 | **0.00** |

### Interpretation

- **C** can reach other services fastest.
- Highly latency-sensitive service.

---

## 4️⃣ Eigenvector Centrality (Undirected)

### Definition

Eigenvector Centrality measures **global influence**.

A node is important if it connects to **other important nodes**.

Mathematically:

Ax = λx


Where:
- A = adjacency matrix
- x = centrality vector

---

### Adjacency Matrix (Undirected)

    A B C D
A [ 0 1 1 0 ]
B [ 1 0 1 0 ]
C [ 1 1 0 1 ]
D [ 0 0 1 0 ]


### Resulting Eigenvector Centrality (Normalized)

| Node | Eigenvector |
|----|-------------|
| A | 0.41 |
| B | 0.41 |
| C | **0.65** |
| D | 0.25 |

### Interpretation

- **C** is connected to other important nodes.
- Failure impacts the whole system.

---

## Final Centrality Feature Vector (ML-Ready)

```json
{
  "A": {
    "degree": 0.67,
    "betweenness": 0.00,
    "closeness": 0.25,
    "eigenvector": 0.41
  },
  "B": {
    "degree": 0.67,
    "betweenness": 0.17,
    "closeness": 0.33,
    "eigenvector": 0.41
  },
  "C": {
    "degree": 1.00,
    "betweenness": 0.33,
    "closeness": 1.00,
    "eigenvector": 0.65
  },
  "D": {
    "degree": 0.33,
    "betweenness": 0.00,
    "closeness": 0.00,
    "eigenvector": 0.25
  }
}

