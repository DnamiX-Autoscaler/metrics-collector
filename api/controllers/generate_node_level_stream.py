import json
import time
from typing import Dict, Any, List

from collectors.node.node_aggregator import collect_node_metrics
from config.settings import WINDOW_SIZE_SECONDS
from utils.time_utils import current_utc_iso
from api.service_targets import NAMESPACE_SERVICES


def generate_node_level_stream():
    """
    SSE generator for real-time node-level metrics
    Output shape EXACTLY matches frontend contract
    """

    while True:
        nodes: List[Dict[str, Any]] = []

        # node_aggregator already returns:
        # { nodeName: { metrics... } }
        node_metrics_map = collect_node_metrics(0, WINDOW_SIZE_SECONDS)

        ts = current_utc_iso()

        for node_name, metrics in node_metrics_map.items():
            node_base = {
                "node_cpu_usage_percent": round(metrics.get("node_cpu_usage_percent", 0.0), 2),
                "node_memory_usage_percent": round(metrics.get("node_memory_usage_percent", 0.0), 2),
                "node_memory_usage_mb": round(metrics.get("node_memory_usage_mb", 0.0), 2),
                "node_network_rx_kbps": round(metrics.get("node_network_rx_kbps", 0.0), 2),
                "node_network_tx_kbps": round(metrics.get("node_network_tx_kbps", 0.0), 2),
                "node_disk_read_iops": round(metrics.get("node_disk_read_iops", 0.0), 2),
                "node_disk_write_iops": round(metrics.get("node_disk_write_iops", 0.0), 2),
            }

            # One entry per namespace, with only that namespace's services
            for namespace, services in NAMESPACE_SERVICES.items():
                nodes.append({
                    "timestamp": ts,
                    "node_name": node_name,
                    "namespace": namespace,
                    "services": services,
                    **node_base,
                })

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(nodes)}\n\n"

        time.sleep(2)  # refresh interval (seconds)
