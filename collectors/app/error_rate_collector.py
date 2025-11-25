# collectors/app/error_rate_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_error_rates(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect:
      - success_rate_percent
      - error_rate_percent
      - http_4xx_rate_percent
      - http_5xx_rate_percent
    """

    window = f"[{window_size_seconds}s]"

    q_total = (
        "sum(rate(istio_request_count{namespace=\"%s\", destination_service=\"%s\"}%s))"
        % (namespace, service_name, window)
    )
    q_4xx = (
        "sum(rate(istio_request_count{namespace=\"%s\", response_code=~\"4.*\", destination_service=\"%s\"}%s))"
        % (namespace, service_name, window)
    )
    q_5xx = (
        "sum(rate(istio_request_count{namespace=\"%s\", response_code=~\"5.*\", destination_service=\"%s\"}%s))"
        % (namespace, service_name, window)
    )

    # Run queries
    total = _run(q_total)
    four_xx = _run(q_4xx)
    five_xx = _run(q_5xx)

    errors = four_xx + five_xx

    return {
        "success_rate_percent": 100.0 - (errors / total * 100 if total > 0 else 0),
        "error_rate_percent": (errors / total * 100 if total > 0 else 0),
        "http_4xx_rate_percent": (four_xx / total * 100 if total > 0 else 0),
        "http_5xx_rate_percent": (five_xx / total * 100 if total > 0 else 0),
    }


def _run(query: str) -> float:
    """Helper for simple single-value query."""
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0.0
