"""
SSE endpoint: 30-second sliding-window traffic features, streamed continuously.

Emits one SSE event every `refresh_seconds` (default = window_seconds = 30).
Each event is identical in shape to the REST /sliding-window/features response
so frontends can consume both with the same parser.

Stream Parameters  (passed as query params to the SSE endpoint)
-----------------------------------------------------------------
window_seconds  — sliding window width in seconds     (default: 30)
sub_step        — sub-interval resolution in seconds  (default: 5)
refresh_seconds — how often to push a new event       (default: same as window_seconds)

SSE endpoint
------------
GET /sliding-window/features/live-stream?window_seconds=30&sub_step=5&refresh_seconds=30
"""

import time
import json
from typing import Generator

from api.controllers.generate_sliding_window import (
    _discover_namespace_services,
    _compute_features,
)


def generate_sliding_window_stream(
    window_seconds: int = 30,
    sub_step: int = 5,
    refresh_seconds: int = 0,   # 0 → default to window_seconds
) -> Generator[str, None, None]:
    """
    SSE generator.
    On each tick:
      1. Re-discovers all namespace/service pairs.
      2. Calls _compute_features() for every service.
      3. Emits one SSE `data:` event as JSON.
      4. Sleeps for `refresh_seconds` before the next tick.
    """

    window_seconds  = max(10, min(window_seconds, 300))
    sub_step        = max(1,  min(sub_step, window_seconds // 2))
    effective_refresh = refresh_seconds if refresh_seconds > 0 else window_seconds

    while True:
        namespace_services = _discover_namespace_services()

        features = []
        for namespace, services in namespace_services.items():
            for svc in services:
                try:
                    row = _compute_features(namespace, svc, window_seconds, sub_step)
                    features.append(row)
                except Exception:
                    pass

        payload = {
            "window_seconds":   window_seconds,
            "sub_step_seconds": sub_step,
            "total_services":   len(features),
            "features":         features,
        }

        yield f"data: {json.dumps(payload)}\n\n"
        time.sleep(effective_refresh)
