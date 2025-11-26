# collectors/mesh/mesh_retry_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_retry_rate(
    namespace: str,
    service_name: str,
    window_size_seconds: int,
) -> Dict[str, float]:
    """
    Retry attempts / failure retries.

    Simple version:
      count 503s as retries.

    PromQL:
      sum(rate(istio_requests_total{
          destination_service="<svc>",
          response_code="503",
          namespace="<ns>"
      }[window]))
    """

    query = (
        "sum(rate(istio_requests_total{"
        f'destination_service="{service_name}", '
        'response_code="503", '
        f'namespace="{namespace}"'
        f"}}[{window_size_seconds}s]))"
    )

    logger.info("Mesh retry rate query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        value = float(data["data"]["result"][0]["value"][1])
    except Exception:
        value = 0.0

    return {
        "mesh_retry_rate_rps": value,
    }
