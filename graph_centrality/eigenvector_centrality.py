# graph_centrality/eigenvector_centrality.py

from typing import Dict
import networkx as nx
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_eigenvector_centrality(G: nx.DiGraph) -> Dict[str, float]:
    """
    Eigenvector centrality → finds "indirectly influential" services.

    - Service is important if it connects to other important services.
    - Use undirected version for numerical stability.

    Returns:
      { "product-service": 0.32, "auth-service": 0.67, ... }
    """

    if G.number_of_nodes() == 0:
        return {}

    UG = G.to_undirected()

    try:
        # Use pure power-iteration method (no scipy required)
        ec = nx.eigenvector_centrality(UG, max_iter=1000, tol=1.0e-6)
    except Exception as e:
        logger.error("Eigenvector centrality failed: %s", e)
        # Fallback to zeros
        return {node: 0.0 for node in UG.nodes()}

    logger.info("Computed eigenvector centrality for %d services", len(ec))
    return ec
