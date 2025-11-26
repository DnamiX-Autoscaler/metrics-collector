# collectors/node/node_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from collectors.node.node_cpu_collector import collect_node_cpu_usage
from collectors.node.node_memory_collector import collect_node_memory_usage
from collectors.node.node_network_collector import collect_node_network_io
from collectors.node.node_disk_collector import collect_node_disk_io

logger = get_logger(__name__)


def collect_node_metrics(
    window_start_ts: float,
    window_size_seconds: int,
) -> Dict[str, Dict[str, Any]]:

    logger.info("Collecting ALL node metrics")

    cpu = collect_node_cpu_usage(window_size_seconds)
    mem = collect_node_memory_usage()
    net = collect_node_network_io(window_size_seconds)
    disk = collect_node_disk_io(window_size_seconds)

    merged = {}

    all_nodes = set(cpu.keys()) | set(mem.keys()) | set(net.keys()) | set(disk.keys())

    for node in all_nodes:
        merged[node] = {
            **cpu.get(node, {}),
            **mem.get(node, {}),
            **net.get(node, {}),
            **disk.get(node, {}),
        }

    return merged
