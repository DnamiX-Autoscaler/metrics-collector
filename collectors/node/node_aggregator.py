# collectors/node/node_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger
from utils.node_name import detect_node_name

from collectors.node.node_cpu_collector import collect_node_cpu_usage
from collectors.node.node_memory_collector import collect_node_memory_usage
from collectors.node.node_network_collector import collect_node_network_io
from collectors.node.node_disk_collector import collect_node_disk_io

logger = get_logger(__name__)


def _merge_metric_map(metric_map: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Combine ALL instance metrics into ONE node metric.
    This solves:
        - multiple network interfaces
        - multiple disk devices
        - multiple cAdvisor instance keys
    """

    merged: Dict[str, float] = {}

    for instance, values in metric_map.items():
        for key, value in values.items():
            try:
                merged[key] = merged.get(key, 0.0) + float(value)
            except:
                merged[key] = merged.get(key, 0.0)

    return merged


def collect_node_metrics(
    window_start_ts: float,
    window_size_seconds: int,
) -> Dict[str, Dict[str, Any]]:

    logger.info("Collecting ALL node metrics...")

    cpu  = collect_node_cpu_usage(window_size_seconds)
    mem  = collect_node_memory_usage()
    net  = collect_node_network_io(window_size_seconds)
    disk = collect_node_disk_io(window_size_seconds)

    # Normalize to single-node name (auto-detected)
    node_key = detect_node_name()

    merged = {
        node_key: {
            **_merge_metric_map(cpu),
            **_merge_metric_map(mem),
            **_merge_metric_map(net),
            **_merge_metric_map(disk),
            "node_name": node_key,
        }
    }

    logger.info("Unified node metrics: %s", merged)
    return merged
