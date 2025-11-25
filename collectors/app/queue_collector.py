# collectors/app/queue_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_queue_metrics(namespace, service_name):

    q_queue = (
        f"sum(app_queue_length{{namespace=\"{namespace}\", service=\"{service_name}\"}})"
    )

    queue = _value(q_queue)

    return {
        "queue_length": queue,
        "application_saturation_percent": (queue * 10) if queue > 0 else 0
    }


def _value(query):
    data = client.get("/api/v1/query", params={"query": query})
    try:
        return float(data["data"]["result"][0]["value"][1])
    except:
        return 0.0
