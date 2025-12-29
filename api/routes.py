from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from api.controllers.get_live_metrics import get_live_metrics
from api.controllers.generate_live_stream import generate_live_stream
from api.controllers.get_live_processes import get_live_processes

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
