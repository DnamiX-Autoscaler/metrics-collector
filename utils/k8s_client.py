# utils/k8s_client.py

from kubernetes import client, config
from utils.logger import get_logger

logger = get_logger(__name__)

_core_v1_api = None


def get_core_v1_api():
    """
    Returns a singleton CoreV1Api client.
    Works both:
      - inside cluster
      - outside cluster (kubeconfig)
    """

    global _core_v1_api

    if _core_v1_api:
        return _core_v1_api

    try:
        # If running inside a pod
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes config")
    except Exception:
        # Local dev (Docker Desktop / AKS / Minikube)
        config.load_kube_config()
        logger.info("Loaded kubeconfig from local environment")

    _core_v1_api = client.CoreV1Api()
    return _core_v1_api
