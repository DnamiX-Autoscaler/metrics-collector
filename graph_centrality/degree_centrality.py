# graph_centrality/degree_centrality.py

from typing import Dict
import networkx as nx
from utils.logger import get_logger

logger = get_logger(__name__)


def compute_degree_centrality(G: nx.DiGraph) -> Dict[str, float]:
    """
    Degree centrality → shows direct dependency magnitude.

    Idea:
      - Convert to undirected graph (we care about how "connected" a service is).
      - Use NetworkX degree_centrality (normalized 0..1).

    Returns:
      { "product-service": 0.42, "order-service": 0.71, ... }
    """

    if G.number_of_nodes() == 0:
        return {}

    # Undirected view captures total neighbourhood
    UG = G.to_undirected()

    dc = nx.degree_centrality(UG)

    logger.info("Computed degree centrality for %d services", len(dc))
    return dc
