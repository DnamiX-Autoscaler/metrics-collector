from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from utils.k8s_client import get_core_v1_api
from api.service_targets import NAMESPACE_SERVICES


def _format_ports(ports) -> str:
    """
    Format ports similar to kubectl output
    Example: 80:30080/TCP,15090:31913/TCP
    """
    result = []

    for p in ports:
        proto = p.protocol
        port = p.port

        if p.node_port:
            result.append(f"{port}:{p.node_port}/{proto}")
        else:
            result.append(f"{port}/{proto}")

    return ",".join(result)


def _calculate_age(created_at) -> str:
    delta = datetime.now(timezone.utc) - created_at
    days = delta.days
    return f"{days}d"


def get_running_services(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    v1 = get_core_v1_api()

    namespaces_to_query = [namespace] if namespace else list(NAMESPACE_SERVICES.keys())

    result = []
    for ns in namespaces_to_query:
        services = v1.list_namespaced_service(namespace=ns)
        for svc in services.items:
            spec = svc.spec
            status = svc.status

            result.append({
                "name": svc.metadata.name,
                "namespace": ns,
                "type": spec.type,
                "clusterIP": spec.cluster_ip,
                "externalIP": (
                    status.load_balancer.ingress[0].ip
                    if status.load_balancer and status.load_balancer.ingress
                    else "<none>"
                ),
                "ports": _format_ports(spec.ports or []),
                "age": _calculate_age(svc.metadata.creation_timestamp),
            })

    return result
