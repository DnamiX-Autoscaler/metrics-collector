# graph_centrality/visualizer.py

from typing import Optional
import networkx as nx
import matplotlib.pyplot as plt
from utils.logger import get_logger

logger = get_logger(__name__)


def draw_service_graph(
    G: nx.DiGraph,
    output_path: Optional[str] = None,
    title: str = "Service Dependency Graph",
):
    """
    Optional: Visualize the service graph for documentation / viva.

    - Node size ~ degree
    - Edge width ~ traffic weight
    """

    if G.number_of_nodes() == 0:
        logger.warning("Graph is empty – nothing to visualize.")
        return

    plt.figure(figsize=(10, 8))

    pos = nx.spring_layout(G, k=0.5, seed=42)

    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1
    node_sizes = [300 + 700 * (degrees[n] / max_degree) for n in G.nodes()]

    edge_weights = [G[u][v].get("weight", 1.0) for u, v in G.edges()]
    max_w = max(edge_weights) if edge_weights else 1.0
    edge_widths = [1 + 4 * (w / max_w) for w in edge_weights]

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, arrows=True, arrowstyle="->")
    nx.draw_networkx_labels(G, pos, font_size=9)

    plt.title(title)
    plt.axis("off")

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
        logger.info("Graph visualization saved to %s", output_path)
    else:
        plt.show()
