from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_queue_metrics(namespace: str, service_name: str) -> Dict[str, float]:

    query = (
        "sum(app_queue_length"
        f'{{service="{service_name}"}})'
    )

    try:
        d = client.get("/api/v1/query", params={"query": query})
        q = float(d["data"]["result"][0]["value"][1])
    except:
        q = 0.0

    return {
        "queue_length": q,
        "application_saturation_percent": q * 10 if q > 0 else 0.0,
    }
