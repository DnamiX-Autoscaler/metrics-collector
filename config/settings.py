# config/settings.py
import os

# -------------------------------------------------------------------
# PROMETHEUS SETTINGS
# -------------------------------------------------------------------
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# namespaces you want to monitor (use list)
TARGET_NAMESPACES = [
    "default",
    "monitoring",
    "store",        # aks-store-demo namespace
]

# -------------------------------------------------------------------
# CLUSTER INFO
# -------------------------------------------------------------------
CLUSTER_ID = os.getenv("CLUSTER_ID", "local-minikube")

# -------------------------------------------------------------------
# OUTPUT DATASET
# -------------------------------------------------------------------
OUTPUT_DATASET_PATH = os.getenv("OUTPUT_DATASET_PATH", "dataset.csv")

# -------------------------------------------------------------------
# SCRAPE INTERVAL + WINDOW SIZE
# -------------------------------------------------------------------
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))

