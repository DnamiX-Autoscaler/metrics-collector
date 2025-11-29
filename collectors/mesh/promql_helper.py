from utils.logger import get_logger
from config.settings import PROMETHEUS_URL
from utils.http_client import HTTPClient

logger = get_logger(__name__)
client = HTTPClient(PROMETHEUS_URL)

def build_query(template: str, name: str, namespace: str, window: int) -> str:
    """
    SAFE — No .format(), no brace escaping issues.
    Only replaces our placeholders: {{name}}, {{namespace}}, {{window}}
    """
    return (
        template
        .replace("{{name}}", name)
        .replace("{{namespace}}", namespace)
        .replace("{{window}}", f"{window}s")
    )

def promql_try_candidates(query_template: str, candidates: list, namespace: str, window_size_seconds: int) -> float:
    """
    Try multiple label variations safely.
    query_template uses our placeholder syntax:
        {{name}}, {{namespace}}, {{window}}
    
    Returns the first non-zero value found, or 0.0 if no data is available.
    """
    logger.debug(f"[PROMQL] Trying {len(candidates)} candidates for template: {query_template}")
    
    for cname in candidates:
        query = build_query(query_template, cname, namespace, window_size_seconds)
        logger.info("[PROMQL] %s", query)

        try:
            data = client.get("/api/v1/query", params={"query": query})
            result = data.get("data", {}).get("result", [])

            if result and len(result) > 0:
                value = float(result[0]["value"][1])
                if value > 0.0:  # Return first non-zero value
                    logger.debug(f"[PROMQL] Found value {value} for candidate '{cname}'")
                    return value
                else:
                    logger.debug(f"[PROMQL] Zero value for candidate '{cname}'")
            else:
                logger.debug(f"[PROMQL] No results for candidate '{cname}'")

        except Exception as e:
            logger.warning("[PROMQL] Query failed for candidate '%s': %s", cname, e)
            continue

    logger.debug(f"[PROMQL] No data found for any candidate in namespace '{namespace}'")
    return 0.0

def promql_single_query(query: str) -> float:
    """
    Execute a single PromQL query and return the value.
    Used for queries that don't need candidate mapping.
    """
    logger.info("[PROMQL] %s", query)
    
    try:
        data = client.get("/api/v1/query", params={"query": query})
        result = data.get("data", {}).get("result", [])

        if result and len(result) > 0:
            value = float(result[0]["value"][1])
            logger.debug(f"[PROMQL] Query returned: {value}")
            return value
        else:
            logger.debug("[PROMQL] Query returned no results")
            return 0.0

    except Exception as e:
        logger.warning("[PROMQL] Query execution failed: %s", e)
        return 0.0