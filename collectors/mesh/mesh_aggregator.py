from typing import Dict, Any
from utils.logger import get_logger

from collectors.mesh.mesh_ingress_traffic import collect_mesh_ingress
from collectors.mesh.mesh_egress_traffic import collect_mesh_egress
from collectors.mesh.mesh_latency_collector import collect_mesh_latency
from collectors.mesh.mesh_retry_collector import collect_mesh_retry_rate
from collectors.mesh.mesh_tcp_collector import collect_mesh_tcp_connections
from collectors.mesh.mesh_tls_error_collector import collect_mesh_tls_errors

logger = get_logger(__name__)

MetricMap = Dict[str, Any]


def collect_mesh_metrics(
    namespace: str,
    service_name: str,
    window_size_seconds: int,
) -> MetricMap:
    """
    Collect all Istio service-mesh metrics for the given service.

    Return keys matching dataset schema:
      - inbound_request_rate_rps
      - outbound_request_rate_rps
      - mesh_latency_p95_ms
      - mesh_retry_rate_rps
      - mesh_tcp_open_connections
      - mesh_tls_error_rate_percent
    """

    logger.info(f"[MESH] Collecting metrics for {namespace}/{service_name}")

    try:
        # Collect all mesh metrics with proper parameter passing
        ingress = collect_mesh_ingress(namespace, service_name, window_size_seconds)
        egress = collect_mesh_egress(namespace, service_name, window_size_seconds)
        latency = collect_mesh_latency(namespace, service_name, window_size_seconds)
        retry = collect_mesh_retry_rate(namespace, service_name, window_size_seconds)
        tcp = collect_mesh_tcp_connections(namespace, service_name, window_size_seconds)
        tls_errors = collect_mesh_tls_errors(namespace, service_name, window_size_seconds)

        combined: MetricMap = {
            **ingress,
            **egress,
            **latency,
            **retry,
            **tcp,
            **tls_errors,
        }

        logger.debug(f"[MESH] Combined metrics for {service_name}: {combined}")
        return combined

    except Exception as e:
        logger.exception(f"[MESH] Failed to collect metrics for {service_name}: {e}")
        # Return safe zeroed metrics to avoid dataset row failure
        return {
            "inbound_request_rate_rps": 0.0,
            "outbound_request_rate_rps": 0.0,
            "mesh_latency_p95_ms": 0.0,
            "mesh_retry_rate_rps": 0.0,
            "mesh_tcp_open_connections": 0.0,
            "mesh_tls_error_rate_percent": 0.0,
        }