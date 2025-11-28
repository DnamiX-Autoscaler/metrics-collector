import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient
from utils.logger import get_logger
from config.settings import QUEUE_TEST_MODE

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)




def collect_queue_metrics(namespace: str, service_name: str) -> Dict[str, float]:


    # TEST FOR DATASET PIPELINE ALSO
    if QUEUE_TEST_MODE:
        logger.warning("[QUEUE-TEST] Injecting synthetic queue_length=5 for dataset")
        return {
            "queue_length": 5.0,
            "application_saturation_percent": 50.0,
        }
    # -----------------------------------

    # Case 1: service-specific
    query_labeled = (
        "sum(app_queue_length"
        f'{{service="{service_name}"}})'
    )

    query_global = "sum(app_queue_length)"

    logger.info(f"[QUEUE] Trying labeled query: {query_labeled}")

    try:
        data = client.get("/api/v1/query", params={"query": query_labeled})
        result = data["data"]["result"]
        if result:
            queue = float(result[0]["value"][1])
            logger.info(f"[QUEUE] Found labeled queue metric = {queue}")
        else:
            raise ValueError("No labeled result → fallback")
    except Exception as e:
        logger.warning(f"[QUEUE] Labeled lookup failed → {e}")
        logger.info(f"[QUEUE] Trying global query: {query_global}")

        try:
            data = client.get("/api/v1/query", params={"query": query_global})
            result = data["data"]["result"]
            queue = float(result[0]["value"][1]) if result else 0.0
        except:
            queue = 0.0

    saturation = queue * 10 if queue > 0 else 0.0

    return {
        "queue_length": queue,
        "application_saturation_percent": saturation,
    }


if __name__ == "__main__":
    print(collect_queue_metrics("default", "order-service"))
