import json
import time
from typing import Dict, Any, List

from collectors.app.app_aggregator import collect_app_metrics
from config.settings import TARGET_NAMESPACES, TARGET_SERVICES, WINDOW_SIZE_SECONDS


def generate_app_level_stream():
    """
    SSE generator for real-time APPLICATION-LEVEL metrics
    Output shape EXACTLY matches frontend contract
    """

    while True:
        app_rows: List[Dict[str, Any]] = []

        for namespace in TARGET_NAMESPACES:
            for service in TARGET_SERVICES:
                metrics = collect_app_metrics(
                    namespace=namespace,
                    service_name=service,
                    window_size_seconds=WINDOW_SIZE_SECONDS,
                )

                app_rows.append({
                    "request_rate_rps": round(metrics.get("request_rate_rps", 0.0), 2),
                    "success_rate_percent": round(metrics.get("success_rate_percent", 0.0), 2),
                    "error_rate_percent": round(metrics.get("error_rate_percent", 0.0), 2),
                    "http_4xx_rate_percent": round(metrics.get("http_4xx_rate_percent", 0.0), 2),
                    "http_5xx_rate_percent": round(metrics.get("http_5xx_rate_percent", 0.0), 2),
                    "latency_p50_ms": round(metrics.get("latency_p50_ms", 0.0), 2),
                    "latency_p95_ms": round(metrics.get("latency_p95_ms", 0.0), 2),
                    "latency_p99_ms": round(metrics.get("latency_p99_ms", 0.0), 2),
                    "queue_length": round(metrics.get("queue_length", 0.0), 2),
                    "application_saturation_percent": round(
                        metrics.get("application_saturation_percent", 0.0), 2
                    ),
                })

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(app_rows)}\n\n"

        time.sleep(2)  # refresh interval (seconds)
