from typing import List, Tuple
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

# (source_service, destination_service, weight_rps)
Edge = Tuple[str, str, float]


def extract_edges(
    namespace: str,
    window_size_seconds: int,
    min_rps_threshold: float = 0.01,
) -> List[Edge]:
    """
    Istio Telemetry v2 compatible edge extractor.

    Uses:
      - source_workload
      - destination_workload

    PromQL:
      sum(
        rate(istio_requests_total{
          namespace="<ns>",
          source_workload!="",
          destination_workload!=""
        }[<window>s])
      ) by (source_workload, destination_workload)
    """

    range_selector = f"[{window_size_seconds}s]"

    query = (
        "sum(rate(istio_requests_total{"
        f'namespace="{namespace}", '
        'source_workload!="", '
        'destination_workload!=""'
        f"}}{range_selector})) by (source_workload, destination_workload)"
    )

    logger.info("Graph edge extractor PromQL: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Edge extraction Prometheus query failed: %s", data)
        return []

    results = data.get("data", {}).get("result", [])
    edges: List[Edge] = []

    for item in results:
        metric = item.get("metric", {})
        src = metric.get("source_workload")
        dst = metric.get("destination_workload")

        if not src or not dst:
            continue

        try:
            rps = float(item.get("value", [None, "0"])[1])
        except (TypeError, ValueError):
            rps = 0.0

        # ultra-low noise edges එලවන්න
        if rps < min_rps_threshold:
            continue

        edges.append((src, dst, rps))

    logger.info("Extracted %d edges from Istio traffic graph", len(edges))
    return edges
