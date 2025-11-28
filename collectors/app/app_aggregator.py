# collectors/app/app_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from collectors.app.rps_collector import collect_rps
from collectors.app.error_rate_collector import collect_error_rates
from collectors.app.latency_collector import collect_latency
from collectors.app.queue_collector import collect_queue_metrics

logger = get_logger(__name__)

MetricMap = Dict[str, Any]


# collectors/app/app_aggregator.py

def collect_app_metrics(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, Any]:

    # Auto-map pod-prefix to service label in metrics
    service_label = service_name.replace("-", "_")

    candidate_labels = [
        service_name,                  # order-service
        service_label,                 # order_service
        service_name.split("-")[0],    # order
    ]

    # Try multiple service labels
    for candidate in candidate_labels:
        rps = collect_rps(namespace, candidate, window_size_seconds)
        if rps.get("request_rate_rps", 0) > 0:
            service_name = candidate
            break

    errors = collect_error_rates(namespace, service_name, window_size_seconds)
    latency = collect_latency(namespace, service_name, window_size_seconds)
    queue = collect_queue_metrics(namespace, service_name)

    metrics = {}
    metrics.update(rps)
    metrics.update(errors)
    metrics.update(latency)
    metrics.update(queue)

    return metrics
