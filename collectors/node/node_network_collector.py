# collectors/node/node_network_collector.py

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def _query_vector(query: str) -> Dict[str, float]:
    logger.info("Querying Prometheus (network): %s", query)
    data = client.get("/api/v1/query", params={"query": query})

    if data.get("status") != "success":
        logger.error("Prometheus network query failed: %s", data)
        return {}

    results = data.get("data", {}).get("result", [])
    out: Dict[str, float] = {}

    for item in results:
        metric = item.get("metric", {})
        value = item.get("value", [None, "0"])[1]
        node_name = metric.get("instance", "unknown-node")
        try:
            val = float(value)
        except (TypeError, ValueError):
            val = 0.0

        out[node_name] = val

    return out


def collect_node_network_io(window_size_seconds: int) -> Dict[str, Dict[str, float]]:
    """
    Collect node-level network RX/TX in kbps.

    PromQL:

      node_network_rx_kbps =
        sum by(instance)(
          irate(node_network_receive_bytes_total{device!~"lo"}[window])
        ) * 8 / 1024

      node_network_tx_kbps =
        sum by(instance)(
          irate(node_network_transmit_bytes_total{device!~"lo"}[window])
        ) * 8 / 1024
    """
    range_selector = f"[{window_size_seconds}s]"

    query_rx = (
        "sum by(instance)("
        f"irate(node_network_receive_bytes_total{{device!~\"lo\"}}{range_selector})"
        ") * 8 / 1024"
    )

    query_tx = (
        "sum by(instance)("
        f"irate(node_network_transmit_bytes_total{{device!~\"lo\"}}{range_selector})"
        ") * 8 / 1024"
    )

    rx_map = _query_vector(query_rx)
    tx_map = _query_vector(query_tx)

    combined: Dict[str, Dict[str, float]] = {}
    all_nodes = set(rx_map.keys()) | set(tx_map.keys())

    for node in all_nodes:
        combined[node] = {
            "node_network_rx_kbps": rx_map.get(node, 0.0),
            "node_network_tx_kbps": tx_map.get(node, 0.0),
        }

    return combined
