# collectors/node/node_network_collector.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    """
    Execute a PromQL query and return:
        { instance: value }
    """
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Network query failed: %s", query)
        return {}

    out = {}
    for item in data["data"].get("result", []):
        instance = item["metric"].get("instance", "unknown")
        raw_val = item.get("value", [None, "0"])[1]
        try:
            out[instance] = float(raw_val)
        except:
            out[instance] = 0.0

    return out


def collect_node_network_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Network I/O per node (Kbps):
        RX = receive bits/sec
        TX = transmit bits/sec
    """

    # RX in Kbps
    rx_query = (
        "sum by(instance)("
        f"irate(node_network_receive_bytes_total{{device!~\"lo|veth.*\"}}[{window_size_seconds}s])"
        ") * 8 / 1024"
    )

    # TX in Kbps
    tx_query = (
        "sum by(instance)("
        f"irate(node_network_transmit_bytes_total{{device!~\"lo|veth.*\"}}[{window_size_seconds}s])"
        ") * 8 / 1024"
    )

    rx_map = _query_vector(rx_query)
    tx_map = _query_vector(tx_query)

    # Normalize to all possible nodes returned
    combined = {}

    for instance in set(rx_map.keys()) | set(tx_map.keys()):
        combined[instance] = {
            "node_network_rx_kbps": rx_map.get(instance, 0.0),
            "node_network_tx_kbps": tx_map.get(instance, 0.0),
        }

    logger.info("Node network metrics collected: %s", combined)
    return combined
