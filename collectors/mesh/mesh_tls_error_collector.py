from typing import Dict
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

def collect_mesh_tls_errors(namespace: str, service_name: str, window_size_seconds: int) -> Dict[str, float]:
    """
    Collect TLS authentication error rate from Istio for the given service.
    """
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(rate(istio_authentication_handshake_errors_total{'
        'destination_service_name="{{name}}", destination_service_namespace="{{namespace}}"}[{{window}}]))'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"mesh_tls_error_rate_percent": value * 100.0}