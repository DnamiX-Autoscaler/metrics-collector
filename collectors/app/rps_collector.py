# collectors/app/rps_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_rps(namespace: str, service_name: str, window_size_seconds: int):

    query = (
        f"sum(rate(app_request_count_total{{namespace=\"{namespace}\", service=\"{service_name}\"}}[{window_size_seconds}s]))"
    )

    logger.info("PromQL RPS: %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    try:
        value = float(data["data"]["result"][0]["value"][1])
    except:
        value = 0.0

    return {
        "request_rate_rps": value
    }
