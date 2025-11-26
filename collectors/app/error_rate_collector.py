# collectors/app/error_rate_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _run_scalar(query: str) -> float:
    """Run a PromQL query expected to return a single scalar value."""
    logger.info("PromQL (error metric): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        return float(data["data"]["result"][0]["value"][1])
    except Exception as e:
        logger.warning("Failed to parse scalar value for query=%s: %s", query, e)
        return 0.0


def collect_error_rates(
    namespace: str,
    service_name: str,
    window_size_seconds: int
) -> Dict[str, float]:
    """
    Collect application-level error metrics.

    Metric sources (app-level Prometheus client):
      app_request_count_total{namespace, service}
      app_error_count_total{namespace, service}

    PromQL:
      total =
        sum(rate(app_request_count_total{namespace="<ns>", service="<svc>"}[window]))

      errors =
        sum(rate(app_error_count_total{namespace="<ns>", service="<svc>"}[window]))

    Note:
      http_4xx_rate_percent and http_5xx_rate_percent are kept 0.0 here,
      because in your design those come from SERVICE MESH layer (Istio),
      not from pure app-level counters.
    """
    window = window_size_seconds

    q_total = (
        "sum(rate(app_request_count_total"
        f'{{namespace="{namespace}", service="{service_name}"}}[{window}s]))'
    )
    q_error = (
        "sum(rate(app_error_count_total"
        f'{{namespace="{namespace}", service="{service_name}"}}[{window}s]))'
    )

    total = _run_scalar(q_total)
    errors = _run_scalar(q_error)

    if total > 0:
        error_rate = (errors / total) * 100.0
        success_rate = (1.0 - (errors / total)) * 100.0
    else:
        error_rate = 0.0
        success_rate = 0.0

    return {
        "success_rate_percent": success_rate,
        "error_rate_percent": error_rate,

        # 4xx / 5xx breakdown will mainly come from Istio (mesh collectors)
        "http_4xx_rate_percent": 0.0,
        "http_5xx_rate_percent": 0.0,
    }
