from typing import List, Dict, Any, Optional
from utils.k8s_client import get_core_v1_api
from api.service_targets import NAMESPACE_SERVICES


def get_running_pods(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    v1 = get_core_v1_api()

    namespaces_to_query = [namespace] if namespace else list(NAMESPACE_SERVICES.keys())

    result = []
    for ns in namespaces_to_query:
        pods = v1.list_namespaced_pod(namespace=ns)
        _append_pods(pods.items, ns, result)

    return result


def _append_pods(pod_items, namespace: str, result: list) -> None:
    for pod in pod_items:
        status = pod.status
        spec = pod.spec

        ready_containers = sum(
            1 for c in status.container_statuses or [] if c.ready
        )
        total_containers = len(status.container_statuses or [])

        restarts = sum(
            c.restart_count for c in status.container_statuses or []
        )

        result.append({
            "name": pod.metadata.name,
            "namespace": namespace,
            "ready": f"{ready_containers}/{total_containers}",
            "status": status.phase or "Unknown",
            "restarts": restarts,
            "age": str(pod.metadata.creation_timestamp),
            "ip": status.pod_ip,
            "node": spec.node_name,
            "nominatedNode": "<none>",
            "readinessGates": "<none>",
        })
