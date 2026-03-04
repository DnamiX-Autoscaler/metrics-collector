"""
REST endpoint: 30-second sliding-window traffic features per service.

Each call computes 8 features for the most recent `window_seconds` of Istio
traffic, derived entirely from Prometheus metrics exported by Envoy sidecars.

Features (one row per namespace/service)
-----------------------------------------
1.  rps_mean              — mean request rate over the window
2.  rps_std               — std-dev of request rate (sampled at sub_step intervals)
3.  unique_source_count   — distinct upstream workloads sending traffic
4.  ratio_4xx             — fraction of requests with 4xx response code
5.  ratio_5xx             — fraction of requests with 5xx response code
6.  latency_mean          — mean request latency in ms over the window
7.  latency_std           — std-dev of per-sub-interval mean latency in ms
8.  inter_arrival_variance— variance of inter-arrival time (1/rps) in seconds²

Query Parameters
----------------
window_seconds  — sliding window width in seconds     (default: 30, min: 10, max: 300)
sub_step        — sub-interval resolution in seconds  (default: 5,  min: 1,  max: 30)

Example Request
---------------
GET /sliding-window/features?window_seconds=30&sub_step=5

Postman Example
---------------
Method : GET
URL    : http://localhost:8000/sliding-window/features
Params :
  window_seconds = 30
  sub_step       = 5
"""

import time
import math
import statistics
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

from fastapi.responses import JSONResponse

from config.settings import PROMETHEUS_URL, SYSTEM_NAMESPACES, discover_services
from utils.http_client import HTTPClient
from utils.k8s_client import get_core_v1_api

client = HTTPClient(PROMETHEUS_URL)


# ---------------------------------------------------------------------------
# JSON safety helper
# ---------------------------------------------------------------------------

def _safe(v: float) -> float:
    """Replace nan / inf with 0.0."""
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return 0.0
    return v


# ---------------------------------------------------------------------------
# Prometheus helpers
# ---------------------------------------------------------------------------

def _instant_query(promql: str) -> List[Dict]:
    """Fire an instant query and return result list."""
    try:
        data = client.get("/api/v1/query", params={"query": promql})
        if data.get("status") != "success":
            return []
        return data.get("data", {}).get("result", [])
    except Exception:
        return []


def _range_query(promql: str, start: float, end: float, step: int) -> List[Dict]:
    """Fire a range query and return result list."""
    try:
        data = client.get("/api/v1/query_range", params={
            "query": promql,
            "start": start,
            "end": end,
            "step": step,
        })
        if data.get("status") != "success":
            return []
        return data.get("data", {}).get("result", [])
    except Exception:
        return []


def _scalar_instant(result: List[Dict]) -> float:
    """Sum all series values from an instant query result."""
    total = 0.0
    for r in result:
        try:
            total += float(r.get("value", [None, "0"])[1])
        except Exception:
            pass
    return _safe(total)


def _series_values(result: List[Dict]) -> List[Tuple[float, float]]:
    """
    Flatten a range-query result into a sorted list of (timestamp, value) pairs,
    summing across all series at each timestamp.
    """
    bucket: Dict[float, float] = {}
    for r in result:
        for ts, val in r.get("values", []):
            try:
                t = float(ts)
                v = float(val)
                if not (math.isnan(v) or math.isinf(v)):
                    bucket[t] = bucket.get(t, 0.0) + v
            except Exception:
                pass
    return sorted(bucket.items())


# ---------------------------------------------------------------------------
# Namespace / service discovery
# ---------------------------------------------------------------------------

def _discover_namespace_services() -> Dict[str, List[str]]:
    """Return {namespace: [service, ...]} for all non-system namespaces."""
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


# ---------------------------------------------------------------------------
# Per-service feature computation
# ---------------------------------------------------------------------------

def _compute_features(
    namespace: str,
    svc: str,
    window_seconds: int,
    sub_step: int,
) -> Dict[str, Any]:
    """
    Compute all 8 sliding-window features for a single namespace/service pair.

    Strategy
    --------
    * Pull sub-interval time series (step = sub_step) over [now-window, now].
      Each series gives ~(window // sub_step) data points.
    * Compute mean / std / variance in Python from the resulting list.
    * Use instant queries for simple ratios (4xx, 5xx, unique_source_count).
    """

    end_ts   = time.time()
    start_ts = end_ts - window_seconds

    dst = f'destination_service_name="{svc}", destination_service_namespace="{namespace}"'

    # ── Sub-interval time series ────────────────────────────────────────────

    # RPS at each sub-interval
    rps_series = _series_values(_range_query(
        f'sum(rate(istio_requests_total{{{dst}}}[{sub_step}s]))',
        start_ts, end_ts, sub_step,
    ))
    rps_vals = [v for _, v in rps_series]

    # Latency numerator (sum) and denominator (count) at each sub-interval
    lat_sum_series = _series_values(_range_query(
        f'sum(rate(istio_request_duration_seconds_sum{{{dst}}}[{sub_step}s]))',
        start_ts, end_ts, sub_step,
    ))
    lat_cnt_series = _series_values(_range_query(
        f'sum(rate(istio_request_duration_seconds_count{{{dst}}}[{sub_step}s]))',
        start_ts, end_ts, sub_step,
    ))

    # Build per-sub-interval mean latency (ms)
    lat_sum_map = {t: v for t, v in lat_sum_series}
    lat_cnt_map = {t: v for t, v in lat_cnt_series}
    lat_vals_ms: List[float] = []
    for ts, _ in lat_sum_series:
        cnt = lat_cnt_map.get(ts, 0.0)
        if cnt > 0:
            lat_vals_ms.append((lat_sum_map[ts] / cnt) * 1000.0)

    # ── Feature: rps_mean, rps_std ───────────────────────────────────────────
    rps_mean = statistics.mean(rps_vals)     if rps_vals else 0.0
    rps_std  = statistics.stdev(rps_vals)    if len(rps_vals) >= 2 else 0.0

    # ── Feature: inter_arrival_variance ─────────────────────────────────────
    # inter-arrival time = 1 / rps per sub-interval; variance of those values
    iat_vals = [1.0 / r for r in rps_vals if r > 0]
    inter_arrival_variance = statistics.variance(iat_vals) if len(iat_vals) >= 2 else 0.0

    # ── Feature: latency_mean, latency_std ──────────────────────────────────
    latency_mean = statistics.mean(lat_vals_ms)  if lat_vals_ms else 0.0
    latency_std  = statistics.stdev(lat_vals_ms) if len(lat_vals_ms) >= 2 else 0.0

    # ── Feature: unique_source_count (instant) ───────────────────────────────
    # Count distinct upstream workloads sending traffic to this service
    src_result = _instant_query(
        f'count(count by (source_workload)(rate(istio_requests_total{{{dst}}}[{window_seconds}s])))'
    )
    unique_source_count = int(_scalar_instant(src_result))

    # ── Feature: ratio_4xx, ratio_5xx (instant) ─────────────────────────────
    total_rps = _scalar_instant(_instant_query(
        f'sum(rate(istio_requests_total{{{dst}}}[{window_seconds}s]))'
    ))
    rps_4xx = _scalar_instant(_instant_query(
        f'sum(rate(istio_requests_total{{{dst}, response_code=~"4.."}}[{window_seconds}s]))'
    ))
    rps_5xx = _scalar_instant(_instant_query(
        f'sum(rate(istio_requests_total{{{dst}, response_code=~"5.."}}[{window_seconds}s]))'
    ))

    ratio_4xx = _safe(rps_4xx / total_rps) if total_rps > 0 else 0.0
    ratio_5xx = _safe(rps_5xx / total_rps) if total_rps > 0 else 0.0

    return {
        "namespace":             namespace,
        "service":               svc,
        "window_seconds":        window_seconds,
        "sub_step_seconds":      sub_step,
        "sample_count":          len(rps_vals),
        "computed_at":           datetime.fromtimestamp(end_ts, tz=timezone.utc).isoformat(),
        # ── 8 features ──
        "rps_mean":              round(_safe(rps_mean),              6),
        "rps_std":               round(_safe(rps_std),               6),
        "unique_source_count":   unique_source_count,
        "ratio_4xx":             round(ratio_4xx,                    6),
        "ratio_5xx":             round(ratio_5xx,                    6),
        "latency_mean_ms":       round(_safe(latency_mean),          4),
        "latency_std_ms":        round(_safe(latency_std),           4),
        "inter_arrival_variance": round(_safe(inter_arrival_variance), 8),
    }


# ---------------------------------------------------------------------------
# Public endpoint handler
# ---------------------------------------------------------------------------

def get_sliding_window_features(
    window_seconds: int = 30,
    sub_step: int = 5,
) -> JSONResponse:
    """
    One-shot REST handler.
    Returns 8 traffic features per service computed over the last `window_seconds`.
    """
    window_seconds = max(10,  min(window_seconds, 300))
    sub_step       = max(1,   min(sub_step, window_seconds // 2))

    namespace_services = _discover_namespace_services()

    features: List[Dict[str, Any]] = []

    for namespace, services in namespace_services.items():
        for svc in services:
            try:
                row = _compute_features(namespace, svc, window_seconds, sub_step)
                features.append(row)
            except Exception:
                pass

    payload = {
        "window_seconds":  window_seconds,
        "sub_step_seconds": sub_step,
        "total_services":  len(features),
        "features":        features,
    }

    return JSONResponse(content=payload)
