from config.settings import (
    PROMETHEUS_URL,
    CLUSTER_ID,
    WINDOW_SIZE_SECONDS,
    SCRAPE_INTERVAL_SECONDS,
    TARGET_NAMESPACES,
    OUTPUT_DATASET_PATH,
)
from api.service_targets import TARGET_SERVICES


def get_runtime_config():
    return {
        "prometheus": {
            "url": PROMETHEUS_URL,
            "scrape_interval_seconds": SCRAPE_INTERVAL_SECONDS,
        },
        "collection_window_seconds": WINDOW_SIZE_SECONDS,
        "targets": {
            "namespaces": TARGET_NAMESPACES,
            "services": TARGET_SERVICES,
        },
        "modes": {
            "queue_test_mode": QUEUE_TEST_MODE,
            "error_test_mode": ERROR_TEST_MODE,
        },
    }
