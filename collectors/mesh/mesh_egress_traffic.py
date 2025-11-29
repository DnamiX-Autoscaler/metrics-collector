from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

logger = get_logger(__name__)

def collect_mesh_egress(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect egress (outbound) traffic metrics from Istio for the given service.
    """
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(rate(istio_requests_total{source_workload="{{name}}", '
        'source_workload_namespace="{{namespace}}"}[{{window}}]))'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"outbound_request_rate_rps": value}