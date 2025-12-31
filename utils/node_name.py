# utils/node_name.py

import socket
from utils.logger import get_logger

logger = get_logger(__name__)


def detect_node_name() -> str:
    """
    Detect node name in a SAFE way.

    Priority:
    1. Hostname (Docker Desktop → docker-desktop)
    2. Fallback static name if detection fails

    This avoids:
    - Prometheus dependency
    - Circular imports
    """

    try:
        hostname = socket.gethostname()
        logger.info("Detected node hostname: %s", hostname)
        return hostname
    except Exception as e:
        logger.warning("Failed to detect node name: %s", e)
        return "unknown-node"
