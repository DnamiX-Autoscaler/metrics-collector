# collectors/mesh/mesh_latency_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_latency(
    namespace: str,
    service_name: str,
    window_size_seconds: int,
) -> Dict[str, float]:
    """
    Mesh service-to-service latency using Istio histogram.

    We use p95 latency (ms):

    PromQL:
      histogram_quantile(
        0.95,
        sum(
          rate(istio_request_duration_milliseconds_bucket{
            destination_service="<service>",
            namespace="<ns>"
          }[window])
        ) by (le)
      )
    """

    query = (
        "histogram_quantile(0.95, "
        "sum(rate(istio_request_duration_milliseconds_bucket{"
        f'destination_service="{service_name}", '
        f'namespace="{namespace}"'
        f"}}[{window_size_seconds}s])) by (le))"
    )

    logger.info("Mesh latency p95 query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        value = float(data["data"]["result"][0]["value"][1])
    except Exception:
        value = 0.0

    return {
        "mesh_latency_p95_ms": value,
    }
