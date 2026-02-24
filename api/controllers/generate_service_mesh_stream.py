import json
import time
from typing import Dict, Any, List

from collectors.mesh.mesh_aggregator import collect_mesh_metrics
from config.settings import WINDOW_SIZE_SECONDS
from utils.time_utils import current_utc_iso
from api.service_targets import NAMESPACE_SERVICES


def generate_service_mesh_stream():
    """
    SSE generator for real-time SERVICE-MESH-LEVEL metrics.
    One row per namespace → service, with timestamp.
    """

    while True:
        mesh_rows: List[Dict[str, Any]] = []
        ts = current_utc_iso()

        for namespace, services in NAMESPACE_SERVICES.items():
            for service in services:
                metrics = collect_mesh_metrics(
                    namespace=namespace,
                    service_name=service,
                    window_size_seconds=WINDOW_SIZE_SECONDS,
                )

                mesh_rows.append({
                    "timestamp": ts,
                    "namespace": namespace,
                    "service_name": service,
                    "inbound_request_rate_rps": round(
                        metrics.get("inbound_request_rate_rps", 0.0), 2
                    ),
                    "outbound_request_rate_rps": round(
                        metrics.get("outbound_request_rate_rps", 0.0), 2
                    ),
                    "mesh_latency_p95_ms": round(
                        metrics.get("mesh_latency_p95_ms", 0.0), 2
                    ),
                    "mesh_retry_rate_rps": round(
                        metrics.get("mesh_retry_rate_rps", 0.0), 2
                    ),
                    "mesh_tcp_open_connections": int(
                        metrics.get("mesh_tcp_open_connections", 0)
                    ),
                    "mesh_tls_error_rate_percent": round(
                        metrics.get("mesh_tls_error_rate_percent", 0.0), 3
                    ),
                })

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(mesh_rows)}\n\n"

        time.sleep(2)  # refresh interval (seconds)
