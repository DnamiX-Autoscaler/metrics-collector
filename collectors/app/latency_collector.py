# collectors/app/latency_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_latency(namespace, service_name, window):

    def q(p):
        return (
            f"histogram_quantile({p}, sum(rate(app_request_duration_ms_bucket{{namespace=\"{namespace}\", service=\"{service_name}\"}}[{window}s])) by (le))"
        )

    return {
        "latency_p50_ms": _value(q(0.5)),
        "latency_p95_ms": _value(q(0.95)),
        "latency_p99_ms": _value(q(0.99)),
    }


def _value(query):
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0.0
