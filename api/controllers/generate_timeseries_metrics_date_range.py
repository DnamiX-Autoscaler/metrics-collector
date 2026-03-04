"""
REST endpoint (non-SSE): Historical metrics for a configurable lookback window.
Fetched once from Prometheus via range queries, one row per timestamp per service.

Query Parameters
----------------
lookback_days   — how many days of history to fetch         (default: 3)
step_seconds    — resolution between data points in seconds (default: 43200 = 12 h)

Returns
-------
JSON object with query_range metadata and per-service timestamped rows.

Example Request
---------------
GET /timeseries/date-range?lookback_days=7&step_seconds=3600

Postman Example
---------------
Method : GET
URL    : http://localhost:8000/timeseries/date-range
Params :
  lookback_days  = 7
  step_seconds   = 3600
"""

import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import Query
from fastapi.responses import JSONResponse

from config.settings import PROMETHEUS_URL, WINDOW_SIZE_SECONDS, SYSTEM_NAMESPACES, discover_services
from utils.http_client import HTTPClient
from utils.k8s_client import get_core_v1_api
from utils.time_features import compute_time_features
from graph_centrality.compute_all import compute_all_centralities

client = HTTPClient(PROMETHEUS_URL)

import math

def _safe(value: float) -> float:
    """Replace nan/inf with 0.0 so the payload is always JSON-serializable."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return 0.0
    return value


# ---------------------------------------------------------------------------
# Internal helpers (identical logic to the SSE version so results are consistent)
# ---------------------------------------------------------------------------

def _range_query(promql: str, start: float, end: float, step: int) -> List[Dict]:
    """Execute a Prometheus range query and return the result list."""
    try:
        data = client.get("/api/v1/query_range", params={
            "query": promql,
            "start": start,
            "end": end,
            "step": step,
        })
        return data.get("data", {}).get("result", [])
    except Exception:
        return []


def _scalar_series(result: List[Dict]) -> Dict[float, float]:
    """Flatten a range query result into {timestamp: value} dict (summed across all series)."""
    series: Dict[float, float] = {}
    for r in result:
        for ts, val in r.get("values", []):
            try:
                series[float(ts)] = series.get(float(ts), 0.0) + float(val)
            except Exception:
                pass
    return series


def _discover_namespace_services() -> Dict[str, List[str]]:
    """Live-discover all non-system namespaces and their services."""
    try:
        v1 = get_core_v1_api()
        all_ns = [n.metadata.name for n in v1.list_namespace().items]
        namespaces = sorted(ns for ns in all_ns if ns not in SYSTEM_NAMESPACES)
    except Exception:
        namespaces = []

    result: Dict[str, List[str]] = {}
    for ns in namespaces:
        try:
            result[ns] = discover_services(ns)
        except Exception:
            result[ns] = []
    return result


def _collect_historical_for_service(
    namespace: str,
    svc: str,
    start: float,
    end: float,
    step: int,
    centrality_map: Dict,
) -> List[Dict[str, Any]]:
    """
    Query Prometheus for all metrics for a single service over [start, end].
    Returns a list of rows, one per step interval.
    """
    ns_svc = f'namespace="{namespace}", service="{svc}"'
    w = WINDOW_SIZE_SECONDS

    # ---- APP metrics ----
    rps = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s]))', start, end, step))
    success = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}, code=~"2.."}}[{w}s])) / '
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s])) * 100', start, end, step))
    error = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}, code=~"5.."}}[{w}s])) / '
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s])) * 100', start, end, step))
    latency_p50 = _scalar_series(_range_query(
        f'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{{{ns_svc}}}[{w}s])) * 1000', start, end, step))
    latency_p95 = _scalar_series(_range_query(
        f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{{ns_svc}}}[{w}s])) * 1000', start, end, step))

    # ---- POD metrics ----
    pod_cpu_avg = _scalar_series(_range_query(
        f'avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod=~"{svc}-.*"}}[{w}s])) * 100', start, end, step))
    pod_cpu_p95 = _scalar_series(_range_query(
        f'quantile(0.95, rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod=~"{svc}-.*"}}[{w}s])) * 100', start, end, step))
    pod_mem_avg = _scalar_series(_range_query(
        f'avg(container_memory_working_set_bytes{{namespace="{namespace}", pod=~"{svc}-.*"}}) / 1048576', start, end, step))
    pod_mem_p95 = _scalar_series(_range_query(
        f'quantile(0.95, container_memory_working_set_bytes{{namespace="{namespace}", pod=~"{svc}-.*"}}) / 1048576', start, end, step))
    pod_count = _scalar_series(_range_query(
        f'count(kube_pod_info{{namespace="{namespace}", pod=~"{svc}-.*"}})', start, end, step))
    pod_restarts = _scalar_series(_range_query(
        f'sum(kube_pod_container_status_restarts_total{{namespace="{namespace}", pod=~"{svc}-.*"}})', start, end, step))

    # ---- MESH metrics (Istio) ----
    mesh_inbound_rps = _scalar_series(_range_query(
        f'sum(rate(istio_requests_total{{destination_service_name="{svc}", destination_service_namespace="{namespace}"}}[{w}s]))', start, end, step))
    mesh_latency_p95 = _scalar_series(_range_query(
        f'histogram_quantile(0.95, rate(istio_request_duration_milliseconds_bucket{{destination_service_name="{svc}", destination_service_namespace="{namespace}"}}[{w}s]))', start, end, step))
    mesh_error_rate = _scalar_series(_range_query(
        f'sum(rate(istio_requests_total{{destination_service_name="{svc}", destination_service_namespace="{namespace}", response_code=~"5.."}}[{w}s]))', start, end, step))

    # ---- Centrality (static) ----
    centrality = centrality_map.get(svc, {})

    # ---- Build rows aligned to STEP timestamps ----
    all_timestamps = sorted(set(
        list(rps.keys()) + list(pod_cpu_avg.keys()) + list(pod_count.keys())
    ))

    rows: List[Dict[str, Any]] = []
    for ts in all_timestamps:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        time_features = compute_time_features(dt)

        rows.append({
            "timestamp": dt.isoformat(),
            "namespace": namespace,
            "service_name": svc,
            "current_pod_count": int(pod_count.get(ts, 0)),

            # APP
            "request_rate_rps": _safe(round(rps.get(ts, 0.0), 4)),
            "success_rate_percent": _safe(round(success.get(ts, 0.0), 2)),
            "error_rate_percent": _safe(round(error.get(ts, 0.0), 4)),
            "latency_p50_ms": _safe(round(latency_p50.get(ts, 0.0), 2)),
            "latency_p95_ms": _safe(round(latency_p95.get(ts, 0.0), 2)),

            # POD
            "pod_cpu_usage_percent_avg": _safe(round(pod_cpu_avg.get(ts, 0.0), 4)),
            "pod_cpu_usage_percent_p95": _safe(round(pod_cpu_p95.get(ts, 0.0), 4)),
            "pod_memory_usage_mb_avg": _safe(round(pod_mem_avg.get(ts, 0.0), 2)),
            "pod_memory_usage_mb_p95": _safe(round(pod_mem_p95.get(ts, 0.0), 2)),
            "pod_restart_count": int(pod_restarts.get(ts, 0)),

            # MESH
            "mesh_inbound_rps": _safe(round(mesh_inbound_rps.get(ts, 0.0), 4)),
            "mesh_inbound_latency_p95_ms": _safe(round(mesh_latency_p95.get(ts, 0.0), 2)),
            "mesh_inbound_error_rate": _safe(round(mesh_error_rate.get(ts, 0.0), 4)),

            # GRAPH CENTRALITY
            "degree_centrality": _safe(round(centrality.get("degree_centrality", 0.0), 3)),
            "betweenness_centrality": _safe(round(centrality.get("betweenness_centrality", 0.0), 3)),
            "closeness_centrality": _safe(round(centrality.get("closeness_centrality", 0.0), 3)),
            "eigenvector_centrality": _safe(round(centrality.get("eigenvector_centrality", 0.0), 3)),

            # TIME FEATURES
            **time_features,
        })

    return rows


# ---------------------------------------------------------------------------
# Public endpoint handler — called directly by the FastAPI route
# ---------------------------------------------------------------------------

def get_timeseries_date_range(
    lookback_days: int = Query(default=3, ge=1, le=90, description="Days of history to fetch (1–90)"),
    step_seconds: int = Query(default=43200, ge=60, le=86400, description="Step resolution in seconds (60–86400)"),
):
    """
    Fetch historical timeseries metrics for all discovered services.

    - **lookback_days**: how many days back from now to query (default 3)
    - **step_seconds**: data-point resolution in seconds (default 43200 = 12 h)
    """
    end_ts = time.time()
    start_ts = end_ts - (lookback_days * 24 * 3600)

    namespace_services = _discover_namespace_services()

    payload: Dict[str, Any] = {
        "query_range": {
            "start": datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat(),
            "end": datetime.fromtimestamp(end_ts, tz=timezone.utc).isoformat(),
            "step_seconds": step_seconds,
            "lookback_days": lookback_days,
        },
        "services": {},
    }

    for namespace, services in namespace_services.items():
        if not services:
            continue

        try:
            centrality_map = compute_all_centralities(
                namespace=namespace,
                window_size_seconds=step_seconds,
            )
        except Exception:
            centrality_map = {}

        for svc in services:
            rows = _collect_historical_for_service(
                namespace, svc, start_ts, end_ts, step_seconds, centrality_map
            )
            if rows:
                payload["services"][f"{namespace}/{svc}"] = rows

    return JSONResponse(content=payload)
