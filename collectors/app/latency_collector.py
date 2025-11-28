from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_latency(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:

    def query(p):
        return (
            f"histogram_quantile({p}, "
            "sum(rate(http_request_duration_milliseconds_bucket"
            f'{{service="{service_name}", namespace="{namespace}"}}[{window_size_seconds}s])) by (le))'
        )

    def fetch(q):
        try:
            d = client.get("/api/v1/query", params={"query": q})
            return float(d["data"]["result"][0]["value"][1])
        except:
            return 0.0

    return {
        "latency_p50_ms": fetch(query(0.50)),
        "latency_p95_ms": fetch(query(0.95)),
        "latency_p99_ms": fetch(query(0.99)),
    }
