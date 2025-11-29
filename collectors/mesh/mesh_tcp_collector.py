from typing import Dict
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

def collect_mesh_tcp_connections(namespace: str, service_name: str, window_size_seconds: int = 30) -> Dict[str, float]:
    """
    Collect active TCP connections from Envoy for the given service.
    Note: window_size_seconds is not used for this instant metric but kept for consistency.
    """
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(envoy_tcp_downstream_cx_active{service="{{name}}", '
        'namespace="{{namespace}}"})'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"mesh_tcp_open_connections": value}