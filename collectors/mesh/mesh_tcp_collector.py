# collectors/mesh/mesh_tcp_collector.py

from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)


def collect_mesh_tcp_connections(namespace: str, service_name: str):
    """
    Get TCP open connections for service.

    PromQL:
      sum(envoy_tcp_downstream_cx_active{service="<svc>"})
    """

    query = (
        f"sum(envoy_tcp_downstream_cx_active{{service=\"{service_name}\", namespace=\"{namespace}\"}})"
    )

    logger.info("Mesh TCP open connections query: %s", query)

    data = client.get("/api/v1/query", params={"query": query})

    try:
        val = float(data["data"]["result"][0]["value"][1])
    except:
        val = 0.0

    return {
        "mesh_tcp_open_connections": val
    }
