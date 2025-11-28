from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_error_rates(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:

    q_total = (
        "sum(rate(http_requests_total"
        f'{{service="{service_name}", namespace="{namespace}"}}[{window_size_seconds}s]))'
    )

    q_error = (
        "sum(rate(http_requests_total"
        f'{{service="{service_name}", namespace="{namespace}", status!~"2.."}}[{window_size_seconds}s]))'
    )

    def _get(q):
        try:
            d = client.get("/api/v1/query", params={"query": q})
            return float(d["data"]["result"][0]["value"][1])
        except:
            return 0.0

    total = _get(q_total)
    errors = _get(q_error)

    if total > 0:
        error_rate = (errors / total) * 100
        success_rate = 100 - error_rate
    else:
        error_rate = 0.0
        success_rate = 0.0

    # 4xx / 5xx breakdown
    q_4xx = (
        "sum(rate(http_requests_total"
        f'{{service="{service_name}", namespace="{namespace}", status=~"4.."}}[{window_size_seconds}s]))'
    )

    q_5xx = (
        "sum(rate(http_requests_total"
        f'{{service="{service_name}", namespace="{namespace}", status=~"5.."}}[{window_size_seconds}s]))'
    )

    _4xx = _get(q_4xx)
    _5xx = _get(q_5xx)

    return {
        "success_rate_percent": success_rate,
        "error_rate_percent": error_rate,
        "http_4xx_rate_percent": (_4xx / total * 100) if total else 0.0,
        "http_5xx_rate_percent": (_5xx / total * 100) if total else 0.0,
    }
