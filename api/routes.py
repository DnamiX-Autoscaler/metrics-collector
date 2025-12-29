from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from api.controllers.get_live_metrics import get_live_metrics
from api.controllers.generate_live_stream import generate_live_stream
from api.controllers.get_live_processes import get_live_processes
from api.controllers.generate_process_stream import generate_process_stream
from api.controllers.generate_cluster_performance_stream import (
    generate_cluster_performance_stream
)
from api.controllers.generate_node_level_stream import generate_node_level_stream

router = APIRouter()


# ----------------------------------------------------
# 1) ONE-TIME METRICS (static fetch)
# ----------------------------------------------------
@router.get("/metrics/live")
def live_metrics_endpoint() -> Dict[str, Any]:
    return get_live_metrics()


# ----------------------------------------------------
# 2) REAL-TIME STREAM (SSE)
# ----------------------------------------------------
@router.get("/metrics/live-stream")
def live_stream():
    """SSE endpoint for continuous streaming."""
    return StreamingResponse(generate_live_stream(), media_type="text/event-stream")

# ----------------------------------------------------
# 3) LIVE PROCESSES INFO
# ----------------------------------------------------
@router.get("/process/live")
def live_process_endpoint():
    return get_live_processes()

#----------------------------------------------------
# 4) REAL-TIME PROCESS STREAM (SSE)
#----------------------------------------------------
@router.get("/process/live-stream")
def process_live_stream():
    return StreamingResponse(
        generate_process_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 5) REAL-TIME CLUSTER PERFORMANCE STREAM (SSE)
#----------------------------------------------------
@router.get("/performance/live-stream")
def performance_live_stream():
    return StreamingResponse(
        generate_cluster_performance_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 6) REAL-TIME NODE-LEVEL METRICS STREAM (SSE)
#----------------------------------------------------    
@router.get("/nodes/live-stream")
def node_live_stream():
    return StreamingResponse(
        generate_node_level_stream(),
        media_type="text/event-stream"
    )