from typing import Dict
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

def collect_mesh_retry_rate(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect retry rate metrics (503 errors) from Istio for the given service.
    """
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(rate(istio_requests_total{destination_service_name="{{name}}", '
        'response_code="503", destination_service_namespace="{{namespace}}"}[{{window}}]))'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"mesh_retry_rate_rps": value}