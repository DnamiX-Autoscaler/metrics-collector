# utils/node_name.py

from utils.http_client import HTTPClient
from config.settings import PROMETHEUS_URL
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def detect_node_name() -> str:
    """
    Universal node name detection:
      - AKS / GKE / EKS → kube_node_info
      - Linux clusters → node_uname_info
      - Docker Desktop → fallback: docker-desktop
    """

    # 1) BEST → Native Kubernetes node name
    q1 = 'kube_node_info'
    data = client.get("/api/v1/query", params={"query": q1})
    if data.get("status") == "success":
        results = data["data"].get("result", [])
        if results:
            node = results[0]["metric"].get("node")
            if node:
                logger.info(f"Detected node name from kube_node_info: {node}")
                return node

    # 2) Linux node exporter
    q2 = 'node_uname_info'
    data = client.get("/api/v1/query", params={"query": q2})
    if data.get("status") == "success":
        results = data["data"].get("result", [])
        if results:
            node = results[0]["metric"].get("nodename")
            if node:
                logger.info(f"Detected node name from node_uname_info: {node}")
                return node

    # 3) Fallback → Docker Desktop
    logger.info("Fallback node name detected: docker-desktop")
    return "docker-desktop"
