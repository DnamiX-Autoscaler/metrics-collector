# graph_centrality/closeness_centrality.py

from typing import Dict
import networkx as nx
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_closeness_centrality(G: nx.DiGraph) -> Dict[str, float]:
    """
    Closeness centrality → how fast delay/faults spread through system.

    - We care about reachability in the call graph.
    - Use directed graph, but NetworkX closeness on DiGraph is fine.
    - Treat as unweighted to avoid instability with 1/weight transforms.

    Returns:
      { "product-service": 0.43, "order-service": 0.58, ... }
    """

    if G.number_of_nodes() == 0:
        return {}

    cc = nx.closeness_centrality(G)

    logger.info("Computed closeness centrality for %d services", len(cc))
    return cc
