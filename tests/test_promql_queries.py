# tests/test_promql_queries.py

import types

def test_node_cpu_promql_query(monkeypatch):
    """
    Smoke test for node CPU collector:
      - Ensures PromQL query is built
      - Ensures it contains node_cpu_seconds_total
    """
    from collectors.node import node_cpu_collector

    captured = {}

    def fake_get(path, params=None):
        captured["path"] = path
        captured["params"] = params or {}
        # Minimal fake Prometheus response
        return {
            "status": "success",
            "data": {
                "result": [
                    {"value": [0, "0.5"]}
                ]
            },
        }

    monkeypatch.setattr(node_cpu_collector.client, "get", fake_get)

    result = node_cpu_collector.collect_node_cpu_usage(
        namespace="demo-ns",
        node_name="demo-node",
        window_size_seconds=60,
    )

    assert "query" in captured["params"]
    assert "node_cpu_seconds_total" in captured["params"]["query"]
    assert "node_cpu_usage_percent" in result


def test_pod_cpu_promql_query(monkeypatch):
    """
    Smoke test for pod CPU collector:
      - Ensures PromQL query uses container_cpu_usage_seconds_total
    """
    from collectors.pod import pod_cpu_collector

    captured = {}

    def fake_get(path, params=None):
        captured["path"] = path
        captured["params"] = params or {}
        return {
            "status": "success",
            "data": {
                "result": [
                    {"value": [0, "0.3"]}
                ]
            },
        }

    monkeypatch.setattr(pod_cpu_collector.client, "get", fake_get)

    result = pod_cpu_collector.collect_pod_cpu(
        namespace="demo-ns",
        service_name="product-service",
        window_size_seconds=60,
    )

    assert "query" in captured["params"]
    assert "container_cpu_usage_seconds_total" in captured["params"]["query"]
    assert "pod_cpu_usage_percent_avg" in result


def test_app_rps_promql_query(monkeypatch):
    """
    Smoke test for app-level RPS collector:
      - Ensures PromQL query uses app_request_count_total
    """
    from collectors.app import rps_collector

    captured = {}

    def fake_get(path, params=None):
        captured["path"] = path
        captured["params"] = params or {}
        return {
            "status": "success",
            "data": {
                "result": [
                    {"value": [0, "15.0"]}
                ]
            },
        }

    monkeypatch.setattr(rps_collector.client, "get", fake_get)

    result = rps_collector.collect_rps(
        namespace="demo-ns",
        service_name="product-service",
        window_size_seconds=60,
    )

    assert "query" in captured["params"]
    assert "app_request_count_total" in captured["params"]["query"]
    assert "request_rate_rps" in result
    assert result["request_rate_rps"] == 15.0
