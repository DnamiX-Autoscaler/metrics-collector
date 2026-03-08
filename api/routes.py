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
from api.controllers.get_runtime_config import get_runtime_config
from api.controllers.get_targets_config import get_targets_config
from api.controllers.get_metrics_config import get_metrics_config
from api.controllers.get_running_pods import get_running_pods
from api.controllers.get_running_services import get_running_services
from api.controllers.get_monitoring_services import get_monitoring_services
from api.controllers.generate_service_timeseries_stream import (
    generate_service_timeseries_stream
)
from api.controllers.generate_resilience_metrics import generate_resilience_metrics
from api.controllers.generate_timeseries_metrics_current_date_to_month import (
    generate_monthly_timeseries_stream
)
from api.controllers.generate_timeseries_metrics_date_range import (
    get_timeseries_date_range
)
from api.controllers.generate_sliding_window import get_sliding_window_features
from api.controllers.generate_sliding_window_stream import generate_sliding_window_stream

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

#----------------------------------------------------
# 12) RUNTIME CONFIGURATION
#----------------------------------------------------    
@router.get("/config/runtime")
def runtime_config():
    return get_runtime_config()

#----------------------------------------------------
# 13) TARGETS CONFIGURATION
#----------------------------------------------------
@router.get("/config/targets")
def targets_config():
    return get_targets_config()

#----------------------------------------------------
# 14) METRICS CONFIGURATION
#----------------------------------------------------
@router.get("/config/metrics")
def metrics_config():
    return get_metrics_config()

#----------------------------------------------------
# 15) RUNNING PODS INFO
#----------------------------------------------------
@router.get("/runtime/pods")
def runtime_pods(namespace: str = None):
    return get_running_pods(namespace)

#----------------------------------------------------
# 16) RUNNING SERVICES INFO
#----------------------------------------------------
@router.get("/runtime/services")
def runtime_services(namespace: str = "default"):
    return get_running_services(namespace)

#----------------------------------------------------
# 17) MONITORING SERVICES INFO
#----------------------------------------------------
@router.get("/runtime/monitoring/services")
def runtime_monitoring_services(namespace: str = "monitoring"):
    return get_monitoring_services(namespace)

#----------------------------------------------------
# 18) REAL-TIME SERVICE TIMESERIES STREAM (SSE) - FOR ML MODEL INPUT
#----------------------------------------------------
@router.get("/timeseries/services/live")
def live_service_timeseries():
    return StreamingResponse(
        generate_service_timeseries_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 19) REAL-TIME RESILIENCE METRICS STREAM (SSE) -
#----------------------------------------------------    
@router.get("/resilience/live-stream")
def resilience_live_stream():
    return StreamingResponse(
        generate_resilience_metrics(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 20) HISTORICAL TIMESERIES STREAM (SSE) - PAST 30 DAYS
#     For ML model input: current date back to 1 month
#----------------------------------------------------
@router.get("/timeseries/monthly/live-stream")
def monthly_timeseries_stream():
    return StreamingResponse(
        generate_monthly_timeseries_stream(),
        media_type="text/event-stream"
    )

#----------------------------------------------------
# 21) HISTORICAL TIMESERIES (REST) - PARAM-DRIVEN DATE RANGE
#     Accepts: lookback_days, step_seconds as query params
#     Returns a single JSON response (no SSE)
#----------------------------------------------------
@router.get("/timeseries/date-range")
def timeseries_date_range(
    lookback_days: int = 3,
    step_seconds: int = 43200,
):
    return get_timeseries_date_range(
        lookback_days=lookback_days,
        step_seconds=step_seconds,
    )

#----------------------------------------------------
# 22) SLIDING-WINDOW FEATURES (REST) - ONE-SHOT
#     8 traffic features per service over last N seconds
#     Accepts: window_seconds, sub_step
#----------------------------------------------------
@router.get("/sliding-window/features")
def sliding_window_features(
    window_seconds: int = 30,
    sub_step: int = 5,
):
    return get_sliding_window_features(
        window_seconds=window_seconds,
        sub_step=sub_step,
    )

#----------------------------------------------------
# 23) SLIDING-WINDOW FEATURES STREAM (SSE) - CONTINUOUS
#     Same 8 features pushed every refresh_seconds
#     Accepts: window_seconds, sub_step, refresh_seconds
#----------------------------------------------------
@router.get("/sliding-window/features/live-stream")
def sliding_window_features_stream(
    window_seconds: int = 30,
    sub_step: int = 5,
    refresh_seconds: int = 0,
):
    return StreamingResponse(
        generate_sliding_window_stream(
            window_seconds=window_seconds,
            sub_step=sub_step,
            refresh_seconds=refresh_seconds,
        ),
        media_type="text/event-stream",
    )
