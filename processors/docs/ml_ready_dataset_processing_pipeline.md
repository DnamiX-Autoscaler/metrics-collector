# ML-Ready Dataset Processing Pipeline

## Purpose of the Processing Layer

The processors layer is responsible for transforming **raw, heterogeneous metrics** collected from:
- Node level
- Pod level
- Application level
- Service mesh level
- Graph centrality
- Scaling decisions

into a **clean, consistent, ML-ready dataset row**.

This layer ensures:
- Data quality
- Schema consistency
- Numerical stability
- Temporal alignment

---

## Overall Processing Flow

The processing pipeline follows these stages:

1. Data Cleaning
2. Metric Merging
3. Dataset Row Construction
4. Stress Index Computation
5. Sliding Window Aggregation

Each stage is modular and independently testable.

---

## 1. Data Cleaning (`data_cleaner.py`)

### Objective

To ensure **all numerical values are safe, valid, and ML-compatible** before being fed into the dataset.

---

### Core Cleaning Operations

#### (a) Safe Type Conversion

Algorithm:
```text
If value is None or invalid:
    replace with default (0.0 or 0)
Else:
    convert to numeric type
