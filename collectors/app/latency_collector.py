# collectors/app/latency_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger
from utils.math_utils import p95, p99, safe_avg

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_latency(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect request latency using Istio histogram:
      istio_request_duration_milliseconds_bucket
    """

    window = f"[{window_size_seconds}s]"

    # Histogram metric time series
    query = (
        "histogram_quantile(0.5, sum(rate(istio_request_duration_milliseconds_bucket"
        "{namespace=\"%s\", destination_service=\"%s\"}%s)) by (le))"
        % (namespace, service_name, window)
    )
    q_p95 = query.replace("0.5", "0.95")
    q_p99 = query.replace("0.5", "0.99")

    p50 = _value(query)
    p95_val = _value(q_p95)
    p99_val = _value(q_p99)

    return {
        "latency_p50_ms": p50,
        "latency_p95_ms": p95_val,
        "latency_p99_ms": p99_val,
    }


def _value(query: str) -> float:
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0.0
