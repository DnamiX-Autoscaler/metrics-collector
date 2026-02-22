"""
Resolves TARGET_SERVICES by calling discover_services() for each TARGET_NAMESPACE.
Import TARGET_SERVICES from here instead of config.settings.
"""

from config.settings import TARGET_NAMESPACES, discover_services

TARGET_SERVICES = []
for _ns in TARGET_NAMESPACES:
    try:
        TARGET_SERVICES.extend(discover_services(_ns))
    except Exception:
        pass

# deduplicate while preserving order
TARGET_SERVICES = list(dict.fromkeys(TARGET_SERVICES))
