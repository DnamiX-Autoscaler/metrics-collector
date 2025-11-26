# collectors/app/queue_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _value(query: str) -> float:
    logger.info("PromQL (queue): %s", query)
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except Exception as e:
        logger.warning("Failed to parse queue value for query=%s: %s", query, e)
        return 0.0


def collect_queue_metrics(namespace: str, service_name: str) -> Dict[str, float]:
    """
    Collect queue length and derive application_saturation_percent.

    Metric source (app-level gauge / summary):
      app_queue_length{namespace="<ns>", service="<svc>"}

    We compute:
      application_saturation_percent = queue_length * 10 (simple heuristic)
    """
    q_queue = (
        "sum(app_queue_length"
        f'{{namespace="{namespace}", service="{service_name}"}})'
    )

    queue = _value(q_queue)

    return {
        "queue_length": queue,
        "application_saturation_percent": (queue * 10.0) if queue > 0 else 0.0,
    }
