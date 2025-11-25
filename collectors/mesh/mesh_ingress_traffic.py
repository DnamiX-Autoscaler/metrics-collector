# collectors/mesh/mesh_ingress_traffic.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_ingress(namespace: str, service_name: str, window_size_seconds: int):
    """
    Inbound traffic → requests received by service
    PromQL:
      sum(rate(istio_requests_total{destination_service="<service>", namespace="<ns>"}[window]))
    """

    query = (
        f"sum(rate(istio_requests_total{{destination_service=\"{service_name}\", namespace=\"{namespace}\"}}"
        f"[{window_size_seconds}s]))"
    )

    logger.info("Mesh ingress traffic query: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except:
        val = 0.0

    return {
        "inbound_request_rate_rps": val
    }
