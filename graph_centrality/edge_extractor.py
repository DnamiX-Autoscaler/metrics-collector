# graph_centrality/edge_extractor.py

from typing import List, Tuple
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

Edge = Tuple[str, str, float]  # (source_service, destination_service, weight_rps)


def extract_edges(
    namespace: str,
    window_size_seconds: int,
    min_rps_threshold: float = 0.01,
) -> List[Edge]:
    """
    Istio metrics → Service-to-service edges.

    Uses Istio metric:
      istio_requests_total{
          source_workload!="",
          destination_service!="",
          namespace="<ns>"
      }

    PromQL:
      sum(
        rate(istio_requests_total{
            source_workload!="",
            destination_service!="",
            namespace="<ns>"
        }[<window>s])
      ) by (source_workload, destination_service)

    Returns:
      [
        ("product-service", "order-service", 12.3),  # 12.3 RPS
        ("order-service", "payment-service", 5.7),
        ...
      ]
    """

    range_selector = f"[{window_size_seconds}s]"
    query = (
        "sum(rate(istio_requests_total{"
        f'namespace="{namespace}", '
        'source_workload!="", '
        'destination_service!=""'
        f"}}{range_selector})) by (source_workload, destination_service)"
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
        dst = metric.get("destination_service")

        if not src or not dst:
            continue

        try:
            rps = float(item.get("value", [None, "0"])[1])
        except (TypeError, ValueError):
            rps = 0.0

        # filter out ultra-low noise edges
        if rps < min_rps_threshold:
            continue

        edges.append((src, dst, rps))

    logger.info("Extracted %d edges from Istio traffic graph", len(edges))
    return edges
