# collectors/mesh/mesh_tls_error_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_tls_errors(namespace: str, service_name: str, window_size_seconds: int):
    """
    TLS handshake / mTLS authentication errors.

    PromQL:
      sum(rate(istio_authentication_handshake_errors_total{
        destination_service="<svc>", namespace="<ns>"
      }[window]))

    """

    query = (
        f"sum(rate(istio_authentication_handshake_errors_total{{destination_service=\"{service_name}\", namespace=\"{namespace}\"}}"
        f"[{window_size_seconds}s]))"
    )

    logger.info("Mesh TLS error rate query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except:
        val = 0.0

    return {
        "mesh_tls_error_rate_percent": val * 100
    }
