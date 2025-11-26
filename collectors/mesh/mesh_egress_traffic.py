# collectors/mesh/mesh_egress_traffic.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_egress(
    namespace: str,
    service_name: str,
    window_size_seconds: int,
) -> Dict[str, float]:
    """
    Outbound traffic → requests SENT by the service (RPS).

    PromQL (Istio):
      sum(rate(istio_requests_total{
          source_workload="<service>",
          namespace="<ns>"
      }[window]))
    """

    query = (
        "sum(rate(istio_requests_total{"
        f'source_workload="{service_name}", '
        f'namespace="{namespace}"'
        f"}}[{window_size_seconds}s]))"
    )

    logger.info("Mesh egress traffic query: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        value = float(data["data"]["result"][0]["value"][1])
    except Exception:
        value = 0.0

    return {
        "outbound_request_rate_rps": value,
    }
