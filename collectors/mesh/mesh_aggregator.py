# collectors/mesh/mesh_aggregator.py

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
    Aggregate ALL service-mesh–level metrics for a given service.

    Returns flat dict with keys matching dataset schema:

      - inbound_request_rate_rps
      - outbound_request_rate_rps
      - mesh_latency_p95_ms
      - mesh_retry_rate_rps
      - mesh_tcp_open_connections
      - mesh_tls_error_rate_percent
    """

    logger.info("Collecting MESH metrics for %s/%s", namespace, service_name)

    ingress = collect_mesh_ingress(namespace, service_name, window_size_seconds)
    egress = collect_mesh_egress(namespace, service_name, window_size_seconds)
    latency = collect_mesh_latency(namespace, service_name, window_size_seconds)
    retry = collect_mesh_retry_rate(namespace, service_name, window_size_seconds)
    tcp = collect_mesh_tcp_connections(namespace, service_name)
    tls_errors = collect_mesh_tls_errors(namespace, service_name, window_size_seconds)

    combined: MetricMap = {}
    combined.update(ingress)
    combined.update(egress)
    combined.update(latency)
    combined.update(retry)
    combined.update(tcp)
    combined.update(tls_errors)

    logger.debug("Mesh metrics combined keys: %s", list(combined.keys()))
    return combined
