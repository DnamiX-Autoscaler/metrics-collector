# collectors/mesh/mesh_retry_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_retry_rate(namespace: str, service_name: str, window_size_seconds: int):
    """
    Istio retry attempts.

    PromQL:
      sum(rate(istio_requests_total{
            destination_service="<svc>",
            response_code="503",
            namespace="<ns>"
      }[window]))
    Retry == failure retry (5xx)
    """

    query = (
        f"sum(rate(istio_requests_total{{destination_service=\"{service_name}\", response_code=\"503\", namespace=\"{namespace}\"}}"
        f"[{window_size_seconds}s]))"
    )

    logger.info("Mesh retry rate query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except:
        val = 0.0

    return {
        "mesh_retry_rate_rps": val
    }
