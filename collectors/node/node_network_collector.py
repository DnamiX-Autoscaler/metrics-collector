# collectors/node/node_network_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    data = client.get("/api/v1/query", params={"query": query})
    if data.get("status") != "success":
        return {}

    out = {}
    for item in data["data"]["result"]:
        instance = item["metric"].get("instance", "unknown-node")
        value = item.get("value", [None, "0"])[1]
        try:
            out[instance] = float(value)
        except:
            out[instance] = 0.0
    return out


def collect_node_network_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    rx_query = (
        "sum by(instance)("
        f"irate(node_network_receive_bytes_total{{device!~\"lo\"}}[{window_size_seconds}s])"
        ") * 8 / 1024"
    )

    tx_query = (
        "sum by(instance)("
        f"irate(node_network_transmit_bytes_total{{device!~\"lo\"}}[{window_size_seconds}s])"
        ") * 8 / 1024"
    )

    rx_map = _query_vector(rx_query)
    tx_map = _query_vector(tx_query)

    combined = {}

    for node in set(rx_map.keys()) | set(tx_map.keys()):
        combined[node] = {
            "node_network_rx_kbps": rx_map.get(node, 0.0),
            "node_network_tx_kbps": tx_map.get(node, 0.0),
        }

    return combined
