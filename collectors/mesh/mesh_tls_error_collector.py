# collectors/mesh/mesh_tls_error_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_tls_errors(
    namespace: str,
    service_name: str,
    window_size_seconds: int,
) -> Dict[str, float]:
    """
    TLS handshake / mTLS authentication errors (Istio).

    PromQL:
      sum(rate(istio_authentication_handshake_errors_total{
          destination_service="<svc>",
          namespace="<ns>"
      }[window]))

    We convert rate → percentage-like value (approx)
    by multiplying 100 (so it's comparable with error_rate_percent).
    """

    query = (
        "sum(rate(istio_authentication_handshake_errors_total{"
        f'destination_service="{service_name}", '
        f'namespace="{namespace}"'
        f"}}[{window_size_seconds}s]))"
    )

    logger.info("Mesh TLS error rate query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        rate_val = float(data["data"]["result"][0]["value"][1])
    except Exception:
        rate_val = 0.0

    # Convert to percent-ish (rate * 100)
    percent_val = rate_val * 100.0

    return {
        "mesh_tls_error_rate_percent": percent_val,
    }
