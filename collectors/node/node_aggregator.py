# collectors/node/node_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from collectors.node.node_cpu_collector import collect_node_cpu_usage
from collectors.node.node_memory_collector import collect_node_memory_usage
from collectors.node.node_network_collector import collect_node_network_io
from collectors.node.node_disk_collector import collect_node_disk_io

logger = get_logger(__name__)

MetricMap = Dict[str, Dict[str, Any]]


def collect_node_metrics(
    window_start_ts: float,
    window_size_seconds: int,
) -> MetricMap:
    """
    High-level aggregator for all node-level metrics.

    Returns:
      {
        "node-1": {
          "node_cpu_usage_percent": ...,
          "node_memory_usage_percent": ...,
          "node_memory_usage_mb": ...,
          "node_network_rx_kbps": ...,
          "node_network_tx_kbps": ...,
          "node_disk_read_iops": ...,
          "node_disk_write_iops": ...
        },
        "node-2": { ... }
      }
    """

    logger.info(
        "Collecting node-level metrics for window_start_ts=%s window_size=%s",
        window_start_ts,
        window_size_seconds,
    )

    cpu_map = collect_node_cpu_usage(window_size_seconds=window_size_seconds)
    mem_map = collect_node_memory_usage()
    net_map = collect_node_network_io(window_size_seconds=window_size_seconds)
    disk_map = collect_node_disk_io(window_size_seconds=window_size_seconds)

    merged: MetricMap = {}
    all_nodes = (
        set(cpu_map.keys())
        | set(mem_map.keys())
        | set(net_map.keys())
        | set(disk_map.keys())
    )

    for node in all_nodes:
        merged[node] = {}
        # CPU
        if node in cpu_map:
            merged[node].update(cpu_map[node])
        # Memory
        if node in mem_map:
            merged[node].update(mem_map[node])
        # Network
        if node in net_map:
            merged[node].update(net_map[node])
        # Disk
        if node in disk_map:
            merged[node].update(disk_map[node])

    return merged
