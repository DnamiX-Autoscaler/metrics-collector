"""
SSE stream: Historical metrics for a configurable lookback window (default: past 3 days).
Fetched from Prometheus via range queries, one row per timestamp per service.
Streams per namespace → service → [timestamped rows], refreshed every 30 seconds.

Developer notes
---------------
LOOKBACK_DAYS   — how many days of history to fetch  (change this to adjust range)
STEP_SECONDS    — resolution between data points      (lower = more points = bigger payload)
REFRESH_SECONDS — how often the SSE stream re-fetches (lower = more frequent updates)
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

from config.settings import PROMETHEUS_URL, WINDOW_SIZE_SECONDS, SYSTEM_NAMESPACES, discover_services
from utils.http_client import HTTPClient
from utils.k8s_client import get_core_v1_api
from utils.time_features import compute_time_features
from graph_centrality.compute_all import compute_all_centralities

client = HTTPClient(PROMETHEUS_URL)

# ── Developer-tunable constants ──────────────────────────────────────────────
# Increase LOOKBACK_DAYS to fetch more history (larger payload).
# Decrease STEP_SECONDS for finer resolution (more rows per service).
# Decrease REFRESH_SECONDS to push updates to the frontend more frequently.
LOOKBACK_DAYS   = 3        # days of history to fetch  (was 30 — reduced for payload size)
STEP_SECONDS    = 12 * 3600        # resolution: 12 h between data points
REFRESH_SECONDS = 60         # SSE re-fetch interval in seconds

# Derived — do not edit manually
LOOKBACK_SECONDS = LOOKBACK_DAYS * 24 * 3600


def _range_query(promql: str, start: float, end: float) -> List[Dict]:
    """Execute a Prometheus range query and return the result list."""
    try:
        data = client.get("/api/v1/query_range", params={
            "query": promql,
            "start": start,
            "end": end,
            "step": STEP_SECONDS,
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
    centrality_map: Dict,
) -> List[Dict[str, Any]]:
    """
    Query Prometheus for all metrics for a single service over [start, end].
    Returns a list of rows, one per STEP_SECONDS interval.
    """
    ns_svc = f'namespace="{namespace}", service="{svc}"'
    w = WINDOW_SIZE_SECONDS

    # ---- APP metrics ----
    rps = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s]))', start, end))
    success = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}, code=~"2.."}}[{w}s])) / '
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s])) * 100', start, end))
    error = _scalar_series(_range_query(
        f'sum(rate(http_requests_total{{{ns_svc}, code=~"5.."}}[{w}s])) / '
        f'sum(rate(http_requests_total{{{ns_svc}}}[{w}s])) * 100', start, end))
    latency_p50 = _scalar_series(_range_query(
        f'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{{{ns_svc}}}[{w}s])) * 1000', start, end))
    latency_p95 = _scalar_series(_range_query(
        f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{{ns_svc}}}[{w}s])) * 1000', start, end))

    # ---- POD metrics ----
    pod_cpu_avg = _scalar_series(_range_query(
        f'avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod=~"{svc}-.*"}}[{w}s])) * 100', start, end))
    pod_cpu_p95 = _scalar_series(_range_query(
        f'quantile(0.95, rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod=~"{svc}-.*"}}[{w}s])) * 100', start, end))
    pod_mem_avg = _scalar_series(_range_query(
        f'avg(container_memory_working_set_bytes{{namespace="{namespace}", pod=~"{svc}-.*"}}) / 1048576', start, end))
    pod_mem_p95 = _scalar_series(_range_query(
        f'quantile(0.95, container_memory_working_set_bytes{{namespace="{namespace}", pod=~"{svc}-.*"}}) / 1048576', start, end))
    pod_count = _scalar_series(_range_query(
        f'count(kube_pod_info{{namespace="{namespace}", pod=~"{svc}-.*"}})', start, end))
    pod_restarts = _scalar_series(_range_query(
        f'sum(kube_pod_container_status_restarts_total{{namespace="{namespace}", pod=~"{svc}-.*"}})', start, end))

    # ---- MESH metrics (Istio) ----
    mesh_inbound_rps = _scalar_series(_range_query(
        f'sum(rate(istio_requests_total{{destination_service_name="{svc}", destination_service_namespace="{namespace}"}}[{w}s]))', start, end))
    mesh_latency_p95 = _scalar_series(_range_query(
        f'histogram_quantile(0.95, rate(istio_request_duration_milliseconds_bucket{{destination_service_name="{svc}", destination_service_namespace="{namespace}"}}[{w}s]))', start, end))
    mesh_error_rate = _scalar_series(_range_query(
        f'sum(rate(istio_requests_total{{destination_service_name="{svc}", destination_service_namespace="{namespace}", response_code=~"5.."}}[{w}s]))', start, end))

    # ---- Centrality (static per tick) ----
    centrality = centrality_map.get(svc, {})

    # ---- Build rows aligned to STEP timestamps ----
    # Use the union of all timestamp keys collected
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
            "request_rate_rps": round(rps.get(ts, 0.0), 4),
            "success_rate_percent": round(success.get(ts, 0.0), 2),
            "error_rate_percent": round(error.get(ts, 0.0), 4),
            "latency_p50_ms": round(latency_p50.get(ts, 0.0), 2),
            "latency_p95_ms": round(latency_p95.get(ts, 0.0), 2),

            # POD
            "pod_cpu_usage_percent_avg": round(pod_cpu_avg.get(ts, 0.0), 4),
            "pod_cpu_usage_percent_p95": round(pod_cpu_p95.get(ts, 0.0), 4),
            "pod_memory_usage_mb_avg": round(pod_mem_avg.get(ts, 0.0), 2),
            "pod_memory_usage_mb_p95": round(pod_mem_p95.get(ts, 0.0), 2),
            "pod_restart_count": int(pod_restarts.get(ts, 0)),

            # MESH
            "mesh_inbound_rps": round(mesh_inbound_rps.get(ts, 0.0), 4),
            "mesh_inbound_latency_p95_ms": round(mesh_latency_p95.get(ts, 0.0), 2),
            "mesh_inbound_error_rate": round(mesh_error_rate.get(ts, 0.0), 4),

            # GRAPH CENTRALITY
            "degree_centrality": round(centrality.get("degree_centrality", 0.0), 3),
            "betweenness_centrality": round(centrality.get("betweenness_centrality", 0.0), 3),
            "closeness_centrality": round(centrality.get("closeness_centrality", 0.0), 3),
            "eigenvector_centrality": round(centrality.get("eigenvector_centrality", 0.0), 3),

            # TIME FEATURES
            **time_features,
        })

    return rows


def generate_monthly_timeseries_stream():
    """
    SSE generator.
    On each tick:
      1. Re-discovers namespaces + services.
      2. Queries Prometheus range API for the past LOOKBACK_DAYS days.
      3. Emits one SSE event: { namespace/service: [rows...], ... }
      4. Sleeps REFRESH_SECONDS before re-fetching.
    """

    while True:
        end_ts = time.time()
        start_ts = end_ts - LOOKBACK_SECONDS

        namespace_services = _discover_namespace_services()
        payload: Dict[str, Any] = {
            "query_range": {
                "start": datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat(),
                "end": datetime.fromtimestamp(end_ts, tz=timezone.utc).isoformat(),
                "step_seconds": STEP_SECONDS,
                "lookback_days": LOOKBACK_DAYS,
            },
            "services": {},
        }

        for namespace, services in namespace_services.items():
            if not services:
                continue

            try:
                centrality_map = compute_all_centralities(namespace, WINDOW_SIZE_SECONDS)
            except Exception:
                centrality_map = {}

            for svc in services:
                try:
                    rows = _collect_historical_for_service(
                        namespace, svc, start_ts, end_ts, centrality_map
                    )
                    payload["services"][f"{namespace}/{svc}"] = {
                        "namespace": namespace,
                        "service_name": svc,
                        "data_points": len(rows),
                        "data": rows,
                    }
                except Exception:
                    payload["services"][f"{namespace}/{svc}"] = {
                        "namespace": namespace,
                        "service_name": svc,
                        "data_points": 0,
                        "data": [],
                    }

        yield f"data: {json.dumps(payload)}\n\n"
        time.sleep(REFRESH_SECONDS)
