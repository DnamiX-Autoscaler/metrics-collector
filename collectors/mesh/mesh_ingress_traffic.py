from collectors.mesh.service_name_mapper import map_mesh_label
from collectors.mesh.promql_helper import promql_try_candidates

def collect_mesh_ingress(namespace, service_name, window_size_seconds):
    candidates = map_mesh_label(service_name)

    query_template = (
        'sum(rate(istio_requests_total{destination_service_name="{{name}}", '
        'destination_service_namespace="{{namespace}}"}[{{window}}]))'
    )

    value = promql_try_candidates(
        query_template, candidates, namespace, window_size_seconds
    )

    return {"inbound_request_rate_rps": value}
