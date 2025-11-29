from utils.logger import get_logger
logger = get_logger(__name__)

def map_mesh_label(service_name: str) -> list:
    """
    Map service names to possible Istio label values.
    Based on the actual services deployed in the cluster.
    """
    
    # Manual mappings based on actual service names seen in kubectl output
    manual_mappings = {
        "store-front": [
            "store-front",        # Direct service name
            "front-end",          # Service appears as "front-end" in kubectl
            "store_front",        # Underscore variant
            "store",              # Short form
        ],
        "store-admin": [
            "store-admin",        # Direct service name
            "store_admin",        # Underscore variant
            "admin",              # Short form
        ],
        "product-service": [
            "product-service",    # Direct service name
            "product_service",    # Underscore variant
            "product",            # Short form
        ],
        "order-service": [
            "order-service",      # Direct service name
            "order_service",      # Underscore variant
            "order",              # Short form
        ],
        # Additional services that might be monitored
        "makeline-service": [
            "makeline-service",
            "makeline_service",
            "makeline",
        ],
        "virtual-customer": [
            "virtual-customer",
            "virtual_customer",
            "customer",
        ],
        "virtual-worker": [
            "virtual-worker",
            "virtual_worker",
            "worker",
        ]
    }

    # Start with manual mappings if available
    if service_name in manual_mappings:
        candidates = manual_mappings[service_name].copy()
    else:
        # Generate automatic variants for unknown services
        candidates = [
            service_name,                           # exact match
            service_name.replace("-", "_"),         # dash to underscore
            service_name.replace("_", "-"),         # underscore to dash
        ]
        
        # Add short form (first part before dash/underscore)
        if "-" in service_name:
            candidates.append(service_name.split("-")[0])
        elif "_" in service_name:
            candidates.append(service_name.split("_")[0])

    # Remove duplicates while preserving order
    final_candidates = []
    for candidate in candidates:
        if candidate not in final_candidates:
            final_candidates.append(candidate)
    
    logger.debug(f"[MAPPER] Service '{service_name}' mapped to candidates: {final_candidates}")
    return final_candidates