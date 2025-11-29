# graph_centrality/edge_extractor.py

from typing import List, Tuple
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

Edge = Tuple[str, str, float]

def extract_edges(
    namespace: str,
    window_size_seconds: int,
    min_rps_threshold: float = 0.01,
) -> List[Edge]:

    range_selector = f"[{window_size_seconds}s]"

    # FIXED QUERY FOR ISTIO 1.17 → 1.27+
    query = (
        "sum(rate(istio_requests_total{"
        f'destination_workload_namespace="{namespace}", '
        'source_workload!="" ,'
        'destination_workload!=""'
        f"}}{range_selector})) by (source_workload, destination_workload)"
    )

    logger.info("Graph edge extractor PromQL: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    results = data.get("data", {}).get("result", [])
    edges: List[Edge] = []

    for item in results:
        metric = item.get("metric", {})
        src = metric.get("source_workload")
        dst = metric.get("destination_workload")

        if not src or not dst:
            continue

        try:
            rps = float(item["value"][1])
        except:
            rps = 0.0

        if rps < min_rps_threshold:
            continue

        edges.append((src, dst, rps))

    logger.info("Extracted %d edges", len(edges))
    return edges
