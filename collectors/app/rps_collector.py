# collectors/app/rps_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_rps(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect HTTP Request Rate (RPS) for service.

    PromQL (Istio / normal app):
      sum(rate(istio_request_count{namespace="<ns>", destination_service="<svc>"}[window]))

    Returns:
      { "request_rate_rps": <float> }
    """
    window = f"[{window_size_seconds}s]"

    query = (
        "sum(rate(istio_request_count"
        "{namespace=\"%s\", destination_service=\"%s\"}%s))"
        % (namespace, service_name, window)
    )

    logger.info("Querying RPS: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        value = float(data["data"]["result"][0]["value"][1])
    except:
        value = 0.0

    return {
        "request_rate_rps": value
    }
