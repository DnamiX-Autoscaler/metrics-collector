from typing import Dict
from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

def collect_mesh_tcp_connections(namespace: str, service_name: str, window_size_seconds: int = 30) -> Dict[str, float]:
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(istio_tcp_connections_opened_total{destination_service_name="{{name}}", '
        'destination_service_namespace="{{namespace}}"}) '
        '- '
        'sum(istio_tcp_connections_closed_total{destination_service_name="{{name}}", '
        'destination_service_namespace="{{namespace}}"})'
    )

    value = promql_try_candidates(query_template, candidates, namespace, window_size_seconds)
    return {"mesh_tcp_open_connections": value}
