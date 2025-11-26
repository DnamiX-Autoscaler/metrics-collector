# collectors/app/latency_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _value(query: str) -> float:
    logger.info("PromQL (latency): %s", query)
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except Exception as e:
        logger.warning("Failed to parse latency value for query=%s: %s", query, e)
        return 0.0


def collect_latency(
    namespace: str,
    service_name: str,
    window_size_seconds: int
) -> Dict[str, float]:
    """
    Collect latency percentiles (p50, p95, p99) in milliseconds.

    Metric source (app-level histogram):
      app_request_duration_ms_bucket{namespace="<ns>", service="<svc>", le="<bucket>"}

    PromQL:
      histogram_quantile(0.95,
        sum(rate(app_request_duration_ms_bucket{...}[window])) by (le)
      )
    """

    def q(p: float) -> str:
        return (
            f"histogram_quantile({p}, "
            "sum(rate(app_request_duration_ms_bucket"
            f'{{namespace="{namespace}", service="{service_name}"}}'
            f"[{window_size_seconds}s])) by (le))"
        )

    return {
        "latency_p50_ms": _value(q(0.5)),
        "latency_p95_ms": _value(q(0.95)),
        "latency_p99_ms": _value(q(0.99)),
    }
