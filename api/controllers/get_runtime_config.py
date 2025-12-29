from config.settings import (
    PROMETHEUS_URL,
    TARGET_NAMESPACES,
    TARGET_SERVICES,
    WINDOW_SIZE_SECONDS,
    SCRAPE_INTERVAL_SECONDS,
    QUEUE_TEST_MODE,
    ERROR_TEST_MODE,
)


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
