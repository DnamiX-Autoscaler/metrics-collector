# graph_centrality/graph_builder.py

from typing import List, Tuple
import networkx as nx
from utils.logger import get_logger
from graph_centrality.edge_extractor import extract_edges

logger = get_logger(__name__)

Edge = Tuple[str, str, float]


def build_service_graph(
    namespace: str,
    window_size_seconds: int,
    min_rps_threshold: float = 0.01,
) -> nx.DiGraph:
    """
    Build a directed weighted service graph:
      - Nodes  = services
      - Edges  = calls between services
      - Weight = RPS (traffic intensity)
    """

    edges: List[Edge] = extract_edges(
        namespace=namespace,
        window_size_seconds=window_size_seconds,
        min_rps_threshold=min_rps_threshold,
    )

    G = nx.DiGraph()

    for src, dst, rps in edges:
        # If multiple metrics exist, accumulate weight
        if G.has_edge(src, dst):
            G[src][dst]["weight"] += rps
        else:
            G.add_edge(src, dst, weight=rps)

    logger.info(
        "Built service graph: %d nodes, %d edges",
        G.number_of_nodes(),
        G.number_of_edges(),
    )
    return G
