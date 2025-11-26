# collectors/app/rps_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_rps(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect Request Rate (RPS) for a given service.

    Metric source (app-level Prometheus client):
      app_request_count_total{namespace="<ns>", service="<svc>"}

    PromQL:
      sum(rate(app_request_count_total{namespace="<ns>", service="<svc>"}[window]))
    """
    query = (
        "sum(rate(app_request_count_total"
        f'{{namespace="{namespace}", service="{service_name}"}}[{window_size_seconds}s]))'
    )

    logger.info("PromQL RPS query: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        value_str = data["data"]["result"][0]["value"][1]
        value = float(value_str)
    except Exception as e:
        logger.warning("Failed to parse RPS value for %s/%s: %s", namespace, service_name, e)
        value = 0.0

    return {
        "request_rate_rps": value
    }
