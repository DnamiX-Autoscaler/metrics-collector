# graph_centrality/betweenness_centrality.py

from typing import Dict
import networkx as nx
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_betweenness_centrality(G: nx.DiGraph) -> Dict[str, float]:
    """
    Betweenness centrality → detects bottlenecks on shortest paths.

    - Use directed graph
    - Weight not used (unweighted shortest paths) for stability.

    Returns:
      { "product-service": 0.12, "payment-service": 0.35, ... }
    """

    if G.number_of_nodes() == 0:
        return {}

    # Unweighted, normalized betweenness
    bc = nx.betweenness_centrality(G, normalized=True, weight=None)

    logger.info("Computed betweenness centrality for %d services", len(bc))
    return bc
