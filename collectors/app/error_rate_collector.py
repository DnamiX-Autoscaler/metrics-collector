# collectors/app/error_rate_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_error_rates(namespace, service_name, window):

    q_total = f"sum(rate(app_request_count_total{{namespace=\"{namespace}\", service=\"{service_name}\"}}[{window}s]))"
    q_error = f"sum(rate(app_error_count_total{{namespace=\"{namespace}\", service=\"{service_name}\"}}[{window}s]))"

    total = _run(q_total)
    errors = _run(q_error)

    return {
        "success_rate_percent": (1 - errors / total) * 100 if total > 0 else 0,
        "error_rate_percent": (errors / total) * 100 if total > 0 else 0,
        "http_4xx_rate_percent": 0,   # NOT from app-level unless app provides
        "http_5xx_rate_percent": 0,   # ditto
    }


def _run(query):
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0.0
