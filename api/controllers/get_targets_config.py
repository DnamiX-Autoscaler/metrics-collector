from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from config.settings import TARGET_NAMESPACES, WINDOW_SIZE_SECONDS


def get_targets_config():
    nodes = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
    node_names = list(nodes.keys())

    pods = {}
    for ns in TARGET_NAMESPACES:
        pod_map = collect_pod_metrics(ns, WINDOW_SIZE_SECONDS)
        pods[ns] = list(pod_map.keys())

    return {
        "nodes": node_names,
        "pods": pods,
    }
