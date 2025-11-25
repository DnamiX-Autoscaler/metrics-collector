# processors/data_merger.py

from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

MetricMap = Dict[str, Any]


def merge_metrics(
    base: MetricMap,
    node_metrics: Optional[MetricMap] = None,
    pod_metrics: Optional[MetricMap] = None,
    app_metrics: Optional[MetricMap] = None,
    mesh_metrics: Optional[MetricMap] = None,
    stress_metrics: Optional[MetricMap] = None,
    centrality_metrics: Optional[MetricMap] = None,
    scaling_decision: Optional[MetricMap] = None,
) -> MetricMap:
    """
    Merge all metric layers into a single flat dict.
    Later cleaned + ordered by dataset_row_builder.
    """

    merged: MetricMap = {}
    merged.update(base or {})

    for m in [
        node_metrics,
        pod_metrics,
        app_metrics,
        mesh_metrics,
        stress_metrics,
        centrality_metrics,
        scaling_decision,
    ]:
        if m:
            merged.update(m)

    logger.debug("Merged metrics keys: %s", list(merged.keys()))
    return merged
