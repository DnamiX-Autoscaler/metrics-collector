from typing import List, Dict
from utils.time_utils import current_utc_iso
from config.settings import TARGET_NAMESPACES, WINDOW_SIZE_SECONDS, CLUSTER_ID
from collectors.node.node_aggregator import collect_node_metrics
from api.service_targets import TARGET_SERVICES


def get_live_processes() -> List[Dict]:
    processes = []

    node_metrics = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
    node_name = list(node_metrics.values())[0].get("node_name", "unknown") if node_metrics else "unknown"

    for namespace in TARGET_NAMESPACES:
        for service in TARGET_SERVICES:
            processes.append({
                "clusterId": CLUSTER_ID,
                "timeStamp": current_utc_iso(),
                "windowSize": WINDOW_SIZE_SECONDS,
                "namespace": namespace,
                "serviceName": service,
                "nodeName": node_name
            })

    return processes
