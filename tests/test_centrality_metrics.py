# tests/test_centrality_metrics.py

import networkx as nx

from graph_centrality.degree_centrality import compute_degree_centrality
from graph_centrality.betweenness_centrality import compute_betweenness_centrality
from graph_centrality.closeness_centrality import compute_closeness_centrality
from graph_centrality.eigenvector_centrality import compute_eigenvector_centrality


def _build_sample_graph():
    """
    A → B → C
    A → C
    C → D

    B and C should be more central than D.
    """
    G = nx.DiGraph()
    G.add_edge("service-a", "service-b", weight=10)
    G.add_edge("service-b", "service-c", weight=5)
    G.add_edge("service-a", "service-c", weight=2)
    G.add_edge("service-c", "service-d", weight=1)
    return G


def test_degree_centrality():
    G = _build_sample_graph()
    dc = compute_degree_centrality(G)

    assert "service-a" in dc
    assert "service-d" in dc
    # service-a and service-c have more connections than d
    assert dc["service-a"] > dc["service-d"]
    assert dc["service-c"] > dc["service-d"]


def test_betweenness_centrality():
    G = _build_sample_graph()
    bc = compute_betweenness_centrality(G)

    # service-b and service-c are on paths between others
    assert bc["service-b"] > 0 or bc["service-c"] > 0
    # leaf node should have near-zero betweenness
    assert bc["service-d"] == 0.0


def test_closeness_centrality():
    G = _build_sample_graph()
    cc = compute_closeness_centrality(G)

    # internal nodes are closer to others than edge nodes
    assert cc["service-b"] >= cc["service-a"]
    assert cc["service-c"] >= cc["service-d"]


def test_eigenvector_centrality():
    G = _build_sample_graph()
    ec = compute_eigenvector_centrality(G)

    # C is highly connected to important nodes
    assert ec["service-c"] >= ec["service-b"]
    # leaf will have smallest influence
    assert ec["service-d"] <= ec["service-a"]
