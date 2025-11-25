# collectors/mesh/mesh_latency_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_latency(namespace: str, service_name: str, window_size_seconds: int):
    """
    Mesh service-to-service latency using Istio histogram.

    PromQL:
      histogram_quantile(0.95,
        sum(rate(istio_request_duration_milliseconds_bucket{
            destination_service="<service>", namespace="<ns>"
        }[window])) by (le)
      )
    """

    q = (
        "histogram_quantile(0.95, "
        f"sum(rate(istio_request_duration_milliseconds_bucket{{destination_service=\"{service_name}\", namespace=\"{namespace}\"}}"
        f"[{window_size_seconds}s])) by (le))"
    )

    logger.info("Mesh latency p95 query: %s", q)

    data = client.get("/api/v1/query", params={"query": q})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except:
        val = 0.0

    return {
        "mesh_latency_p95_ms": val
    }
