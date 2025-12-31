# config/settings.py

import os
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
# TARGET NAMESPACES
# -------------------------------------------------------
_raw_namespaces = os.getenv("TARGET_NAMESPACES")
TARGET_NAMESPACES = (
    [ns.strip() for ns in _raw_namespaces.split(",")]
    if _raw_namespaces
    else ["default"]
)

# -------------------------------------------------------
# TARGET SERVICES (LIVE DISCOVERY FROM K8s)
# -------------------------------------------------------
def _discover_services(namespaces):
    v1 = get_core_v1_api()
    services = set()

    for ns in namespaces:
        for svc in v1.list_namespaced_service(ns).items:
            name = svc.metadata.name

            # Skip system / infra services
            if name.startswith(("kubernetes", "prometheus", "istio")):
                continue

            services.add(name)

    return sorted(services)


TARGET_SERVICES = _discover_services(TARGET_NAMESPACES)

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
