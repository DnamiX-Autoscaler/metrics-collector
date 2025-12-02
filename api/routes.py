from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from api.controllers.get_live_metrics import get_live_metrics
from api.controllers.generate_live_stream import generate_live_stream

router = APIRouter()


# ----------------------------------------------------
# 1) OLD ENDPOINT — ONE-TIME METRICS (static fetch)
# ----------------------------------------------------
@router.get("/metrics/live")
def live_metrics_endpoint() -> Dict[str, Any]:
    return get_live_metrics()


# ----------------------------------------------------
# 2) NEW ENDPOINT — REAL-TIME STREAM (SSE)
# ----------------------------------------------------
@router.get("/metrics/live-stream")
def live_stream():
    """SSE endpoint for continuous streaming."""
    return StreamingResponse(generate_live_stream(), media_type="text/event-stream")
