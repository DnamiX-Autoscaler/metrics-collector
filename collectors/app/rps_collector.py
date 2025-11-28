from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_rps(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect RPS using standard Prometheus metric:
      http_requests_total{service="<svc>"}
    """

    query = (
        "sum(rate(http_requests_total"
        f'{{service="{service_name}", namespace="{namespace}"}}[{window_size_seconds}s]))'
    )

    logger.info("RPS Query: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except Exception:
        val = 0.0

    return {"request_rate_rps": val}
