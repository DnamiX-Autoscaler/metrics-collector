# config/settings.py

import os
from typing import List, Set
from utils.k8s_client import get_core_v1_api
from utils.node_name import detect_node_name

# -------------------------------------------------------
# PROMETHEUS (SAFE DEFAULT + ENV OVERRIDE)
# -------------------------------------------------------
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# -------------------------------------------------------
# CLUSTER ID (derived, not hard-coded)
# -------------------------------------------------------
CLUSTER_ID = os.getenv("CLUSTER_ID") or detect_node_name()

# -------------------------------------------------------
# WINDOW & SCRAPE SETTINGS
# -------------------------------------------------------
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))

# -------------------------------------------------------
# NAMESPACE SETTINGS
# -------------------------------------------------------
SYSTEM_NAMESPACES = {
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "monitoring",
    "istio-system",
}

_raw_namespaces = os.getenv("TARGET_NAMESPACES")
TARGET_NAMESPACES = (
    [ns.strip() for ns in _raw_namespaces.split(",") if ns.strip()]
    if _raw_namespaces
    else ["default"]
)

AUTO_DISCOVER_NAMESPACES = os.getenv("AUTO_DISCOVER_NAMESPACES", "0") == "1"

def discover_namespaces() -> List[str]:
    """
    If AUTO_DISCOVER_NAMESPACES=1 -> discover all namespaces except system ones.
    Else -> use TARGET_NAMESPACES.
    """
    if not AUTO_DISCOVER_NAMESPACES:
        return TARGET_NAMESPACES

    v1 = get_core_v1_api()
    all_ns = [n.metadata.name for n in v1.list_namespace().items]
    filtered = [n for n in all_ns if n not in SYSTEM_NAMESPACES]
    return sorted(filtered)

# -------------------------------------------------------
# SERVICE DISCOVERY (PER NAMESPACE)
# -------------------------------------------------------
SKIP_SERVICE_PREFIXES = ("kubernetes", "prometheus", "istio")

def discover_services(namespace: str) -> List[str]:
    """
    Discover services in the given namespace using K8s API.
    Returns service names only.
    """
    v1 = get_core_v1_api()
    services: Set[str] = set()

    for svc in v1.list_namespaced_service(namespace).items:
        name = svc.metadata.name or ""
        if not name:
            continue

        if name.startswith(SKIP_SERVICE_PREFIXES):
            continue

        # optional: skip headless services if needed
        # if svc.spec.cluster_ip == "None":
        #     continue

        services.add(name)

    return sorted(services)

# -------------------------------------------------------
# OUTPUT
# -------------------------------------------------------
OUTPUT_DATASET_PATH = os.getenv("OUTPUT_DATASET_PATH", "dataset.csv")

# -------------------------------------------------------
# FEATURE FLAGS
# -------------------------------------------------------
QUEUE_TEST_MODE = os.getenv("QUEUE_TEST_MODE", "0") == "1"
ERROR_TEST_MODE = os.getenv("ERROR_TEST_MODE", "0") == "1"
CHAOS_MODE = os.getenv("CHAOS_MODE", "0") == "1"
