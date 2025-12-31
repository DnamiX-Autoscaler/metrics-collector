from typing import List, Dict, Any
from utils.k8s_client import get_core_v1_api


def get_running_pods(namespace: str = "default") -> List[Dict[str, Any]]:
    v1 = get_core_v1_api()

    pods = v1.list_namespaced_pod(namespace=namespace)
    result = []

    for pod in pods.items:
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
            "ready": f"{ready_containers}/{total_containers}",
            "status": status.phase or "Unknown",
            "restarts": restarts,
            "age": str(pod.metadata.creation_timestamp),
            "ip": status.pod_ip,
            "node": spec.node_name,
            "nominatedNode": "<none>",
            "readinessGates": "<none>",
        })

    return result
