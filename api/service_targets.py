"""
Resolves TARGET_SERVICES by discovering services across all non-system namespaces.
Import TARGET_SERVICES and TARGET_NAMESPACES from here instead of config.settings
when you need the full multi-namespace list.
"""

from config.settings import (
    SYSTEM_NAMESPACES,
    discover_services,
    TARGET_NAMESPACES as _CONFIGURED_NAMESPACES,
)
from utils.k8s_client import get_core_v1_api

def _discover_all_namespaces():
    """Discover all non-system namespaces from K8s."""
    try:
        v1 = get_core_v1_api()
        all_ns = [n.metadata.name for n in v1.list_namespace().items]
        filtered = [ns for ns in all_ns if ns not in SYSTEM_NAMESPACES]
        return sorted(filtered) if filtered else _CONFIGURED_NAMESPACES
    except Exception:
        return _CONFIGURED_NAMESPACES


# All non-system namespaces
ALL_NAMESPACES = _discover_all_namespaces()

# Collect services from every discovered namespace
TARGET_SERVICES = []
NAMESPACE_SERVICES: dict = {}  # namespace -> [services]

for _ns in ALL_NAMESPACES:
    try:
        _svcs = discover_services(_ns)
        NAMESPACE_SERVICES[_ns] = _svcs
        TARGET_SERVICES.extend(_svcs)
    except Exception:
        NAMESPACE_SERVICES[_ns] = []

# Deduplicate while preserving order
TARGET_SERVICES = list(dict.fromkeys(TARGET_SERVICES))
