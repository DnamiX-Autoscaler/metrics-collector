from typing import List, Dict, Any
from datetime import datetime, timezone

from utils.k8s_client import get_core_v1_api


def _format_ports(ports) -> str:
    result = []

    for p in ports or []:
        proto = p.protocol
        port = p.port

        if p.node_port:
            result.append(f"{port}:{p.node_port}/{proto}")
        else:
            result.append(f"{port}/{proto}")

    return ",".join(result)


def _calculate_age(created_at) -> str:
    delta = datetime.now(timezone.utc) - created_at
    return f"{delta.days}d"


def get_monitoring_services(namespace: str = "monitoring") -> List[Dict[str, Any]]:
    v1 = get_core_v1_api()
    services = v1.list_namespaced_service(namespace=namespace)

    result = []

    for svc in services.items:
        spec = svc.spec
        status = svc.status

        external_ip = "<none>"
        if status and status.load_balancer and status.load_balancer.ingress:
            ingress = status.load_balancer.ingress[0]
            external_ip = ingress.ip or ingress.hostname or "<none>"

        result.append({
            "name": svc.metadata.name,
            "type": spec.type,
            "clusterIP": spec.cluster_ip,
            "externalIP": external_ip,
            "ports": _format_ports(spec.ports),
            "age": _calculate_age(svc.metadata.creation_timestamp),
        })

    return result
