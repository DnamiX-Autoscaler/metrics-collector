# collectors/node/node_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger
from utils.node_name import detect_node_name

from collectors.node.node_cpu_collector import collect_node_cpu_usage
from collectors.node.node_memory_collector import collect_node_memory_usage
from collectors.node.node_network_collector import collect_node_network_io
from collectors.node.node_disk_collector import collect_node_disk_io

logger = get_logger(__name__)


def collect_node_metrics(
    window_start_ts: float,
    window_size_seconds: int,
) -> Dict[str, Dict[str, Any]]:

    logger.info("Collecting ALL node metrics...")

    cpu = collect_node_cpu_usage(window_size_seconds)
    mem = collect_node_memory_usage()
    net = collect_node_network_io(window_size_seconds)
    disk = collect_node_disk_io(window_size_seconds)

    # REAL node name detection
    node_key = detect_node_name()

    # Try matching collected metrics to node name
    cpu_vals = next(iter(cpu.values()), {})
    mem_vals = next(iter(mem.values()), {})
    net_vals = next(iter(net.values()), {})
    disk_vals = next(iter(disk.values()), {})

    merged = {
        node_key: {
            **cpu_vals,
            **mem_vals,
            **net_vals,
            **disk_vals,
            "node_name": node_key,
        }
    }

    logger.info("Unified node metrics: %s", merged)
    return merged
