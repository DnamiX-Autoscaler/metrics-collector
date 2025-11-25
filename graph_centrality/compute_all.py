# graph_centrality/compute_all.py

from typing import Dict, Any
import networkx as nx
from utils.logger import get_logger

from graph_centrality.graph_builder import build_service_graph
from graph_centrality.degree_centrality import compute_degree_centrality
from graph_centrality.betweenness_centrality import compute_betweenness_centrality
from graph_centrality.closeness_centrality import compute_closeness_centrality
from graph_centrality.eigenvector_centrality import compute_eigenvector_centrality

logger = get_logger(__name__)

CentralityRow = Dict[str, float]
CentralityMap = Dict[str, CentralityRow]


def compute_all_centralities(
    namespace: str,
    window_size_seconds: int,
    min_rps_threshold: float = 0.01,
) -> CentralityMap:
    """
    MASTER function – this is where your novelty lives.

    1) Build service-level dependency graph from Istio traffic (G)
    2) Compute 4 centrality measures:
         - degree_centrality
         - betweenness_centrality
         - closeness_centrality
         - eigenvector_centrality
    3) Merge into ML-ready dictionary:

       {
         "product-service": {
            "degree_centrality": ...,
            "betweenness_centrality": ...,
            "closeness_centrality": ...,
            "eigenvector_centrality": ...
         },
         "order-service": { ... }
       }
    """

    logger.info(
        "Computing all centralities for namespace=%s window=%ss",
        namespace,
        window_size_seconds,
    )

    G: nx.DiGraph = build_service_graph(
        namespace=namespace,
        window_size_seconds=window_size_seconds,
        min_rps_threshold=min_rps_threshold,
    )

    degree = compute_degree_centrality(G)
    between = compute_betweenness_centrality(G)
    close = compute_closeness_centrality(G)
    eigen = compute_eigenvector_centrality(G)

    services = set(G.nodes())
    result: CentralityMap = {}

    for svc in services:
        result[svc] = {
            "degree_centrality": degree.get(svc, 0.0),
            "betweenness_centrality": between.get(svc, 0.0),
            "closeness_centrality": close.get(svc, 0.0),
            "eigenvector_centrality": eigen.get(svc, 0.0),
        }

    logger.info("Centrality map built for %d services", len(result))
    return result
