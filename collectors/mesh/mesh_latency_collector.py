from typing import Dict
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates
from utils.logger import get_logger

logger = get_logger(__name__)

def collect_mesh_latency(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect P95 latency metrics from Istio for the given service.
    """
    candidates = map_mesh_label(service_name)

    query_template = (
        'histogram_quantile(0.95, sum(rate('
        'istio_request_duration_milliseconds_bucket{destination_service_name="{{name}}", '
        'destination_service_namespace="{{namespace}}"}[{{window}}])) by (le))'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"mesh_latency_p95_ms": value}