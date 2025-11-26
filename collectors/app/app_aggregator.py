# collectors/app/app_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from collectors.app.rps_collector import collect_rps
from collectors.app.error_rate_collector import collect_error_rates
from collectors.app.latency_collector import collect_latency
from collectors.app.queue_collector import collect_queue_metrics

logger = get_logger(__name__)

MetricMap = Dict[str, Any]


def collect_app_metrics(
    namespace: str,
    service_name: str,
    window_size_seconds: int
) -> MetricMap:
    """
    FINAL APP-LEVEL METRICS AGGREGATOR (Prometheus app-client based).

    Collects:
      ✔ request_rate_rps
      ✔ success_rate_percent
      ✔ error_rate_percent
      ✔ http_4xx_rate_percent
      ✔ http_5xx_rate_percent
      ✔ latency_p50_ms
      ✔ latency_p95_ms
      ✔ latency_p99_ms
      ✔ queue_length
      ✔ application_saturation_percent
    """

    logger.info(
        "Collecting APP metrics for service=%s in namespace=%s (window=%ss)",
        service_name,
        namespace,
        window_size_seconds,
    )

    rps = collect_rps(namespace, service_name, window_size_seconds)
    errors = collect_error_rates(namespace, service_name, window_size_seconds)
    latency = collect_latency(namespace, service_name, window_size_seconds)
    queue = collect_queue_metrics(namespace, service_name)

    metrics: MetricMap = {}
    metrics.update(rps)
    metrics.update(errors)
    metrics.update(latency)
    metrics.update(queue)

    logger.info("APP metrics collected for %s/%s", namespace, service_name)
    return metrics
