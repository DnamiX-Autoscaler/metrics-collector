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
from api.controllers.generate_pod_level_stream import generate_pod_level_stream
from api.controllers.generate_app_level_stream import generate_app_level_stream
from api.controllers.generate_service_mesh_stream import (
    generate_service_mesh_stream
)
from api.controllers.generate_graph_centrality_stream import (
    generate_graph_centrality_stream
)
from api.controllers.generate_stress_index_stream import (
    generate_stress_index_stream
)

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

#----------------------------------------------------
# 7) REAL-TIME POD-LEVEL METRICS STREAM (SSE)
#----------------------------------------------------
@router.get("/pods/live-stream")
def pod_live_stream():
    return StreamingResponse(
        generate_pod_level_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 8) REAL-TIME APP-LEVEL METRICS STREAM (SSE)
#----------------------------------------------------
@router.get("/apps/live-stream")
def app_live_stream():
    return StreamingResponse(
        generate_app_level_stream(),
        media_type="text/event-stream"
    )
 
#----------------------------------------------------
# 9) REAL-TIME SERVICE MESH METRICS STREAM (SSE)
#----------------------------------------------------
@router.get("/mesh/live-stream")
def mesh_live_stream():
    return StreamingResponse(
        generate_service_mesh_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 10) REAL-TIME GRAPH CENTRALITY METRICS STREAM (SSE)
#----------------------------------------------------    
@router.get("/graph/centrality/live-stream")
def graph_centrality_live_stream():
    return StreamingResponse(
        generate_graph_centrality_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 11) REAL-TIME STRESS INDEX + SCALING SIGNALS STREAM (SSE)
#----------------------------------------------------    
@router.get("/stress-index/live-stream")
def stress_index_live_stream():
    return StreamingResponse(
        generate_stress_index_stream(),
        media_type="text/event-stream"
    )