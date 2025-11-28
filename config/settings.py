# config/settings.py
import os

# -------------------------------------------------------------------
# PROMETHEUS SETTINGS
# -------------------------------------------------------------------
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# -------------------------------------------------------------------
# TARGET NAMESPACES IN YOUR CLUSTER
# -------------------------------------------------------------------
# All your microservices run in "default"
TARGET_NAMESPACES = [
    "default"
]

# -------------------------------------------------------------------
# TARGET SERVICES TO COLLECT METRICS FROM
# -------------------------------------------------------------------
TARGET_SERVICES = [
    "store-front",
    "store-admin",
    "product-service",
    "order-service"
]

# -------------------------------------------------------------------
# CLUSTER INFO
# -------------------------------------------------------------------
CLUSTER_ID = os.getenv("CLUSTER_ID", "local-docker-desktop")

# -------------------------------------------------------------------
# OUTPUT DATASET
# -------------------------------------------------------------------
OUTPUT_DATASET_PATH = os.getenv("OUTPUT_DATASET_PATH", "dataset.csv")

# -------------------------------------------------------------------
# SCRAPE INTERVAL + WINDOW SIZE (YOU CAN INCREASE LATER)
# -------------------------------------------------------------------
SCRAPE_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", 30))
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", 30))

# -------------------------------------------------------------------
# TESTING OVERRIDES
# -------------------------------------------------------------------

QUEUE_TEST_MODE = os.getenv("QUEUE_TEST_MODE", "0") == "1"
ERROR_TEST_MODE = os.getenv("ERROR_TEST_MODE", "0") == "1"

