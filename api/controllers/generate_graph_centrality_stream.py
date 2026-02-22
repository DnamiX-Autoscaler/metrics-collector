import json
import time
from typing import Dict, Any, List

from graph_centrality.compute_all import compute_all_centralities
from graph_centrality.graph_builder import build_service_graph
from collectors.app.app_aggregator import collect_app_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from config.settings import TARGET_NAMESPACES, WINDOW_SIZE_SECONDS
from api.service_targets import TARGET_SERVICES


def generate_graph_centrality_stream():
    """
    SSE generator for real-time SERVICE GRAPH + CENTRALITY metrics
    """

    while True:
        services: List[Dict[str, Any]] = []
        connections: List[Dict[str, Any]] = []

        namespace = TARGET_NAMESPACES[0]

        # 1️⃣ Build dependency graph
        G = build_service_graph(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
        )

        # 2️⃣ Centrality metrics
        centrality_map = compute_all_centralities(
            namespace=namespace,
            window_size_seconds=WINDOW_SIZE_SECONDS,
        )

        # 3️⃣ Build service nodes
        for svc in TARGET_SERVICES:
            c = centrality_map.get(svc, {})

            app = collect_app_metrics(namespace, svc, WINDOW_SIZE_SECONDS)
            pod_map = collect_pod_metrics(namespace, WINDOW_SIZE_SECONDS)

            cpu = app.get("application_saturation_percent", 0.0)
            mem = app.get("application_saturation_percent", 0.0)  # safe proxy

            risk = (
                "high" if c.get("betweenness_centrality", 0) > 0.8
                else "medium" if c.get("betweenness_centrality", 0) > 0.6
                else "low"
            )

            status = (
                "critical" if risk == "high"
                else "warning" if risk == "medium"
                else "healthy"
            )

            services.append({
                "id": svc,
                "name": svc.replace("-", " ").title(),
                "degree_centrality": round(c.get("degree_centrality", 0.0), 3),
                "betweenness_centrality": round(c.get("betweenness_centrality", 0.0), 3),
                "closeness_centrality": round(c.get("closeness_centrality", 0.0), 3),
                "eigenvector_centrality": round(c.get("eigenvector_centrality", 0.0), 3),
                "dependencies": G.in_degree(svc) if svc in G else 0,
                "bottleneck_score": round(c.get("betweenness_centrality", 0.0), 3),
                "latency_propagation_speed": round(c.get("closeness_centrality", 0.0), 3),
                "influence_strength": round(c.get("eigenvector_centrality", 0.0), 3),
                "cpu_usage": round(cpu, 2),
                "memory_usage": round(mem, 2),
                "request_rate": round(app.get("request_rate_rps", 0.0), 2),
                "avg_latency": round(app.get("latency_p50_ms", 0.0), 2),
                "status": status,
                "risk_level": risk,
            })

        # 4️⃣ Graph edges
        for u, v, data in G.edges(data=True):
            connections.append({
                "source": u,
                "target": v,
                "weight": round(data.get("weight", 1.0), 2),
            })

        # 5️⃣ Insights
        insights = {
            "total_services": len(services),
            "critical_services": len([s for s in services if s["status"] == "critical"]),
            "high_risk_services": len([s for s in services if s["risk_level"] == "high"]),
            "bottleneck_services": len([s for s in services if s["bottleneck_score"] > 0.7]),
            "avg_degree_centrality": round(
                sum(s["degree_centrality"] for s in services) / len(services), 3
            ) if services else 0.0,
            "avg_betweenness_centrality": round(
                sum(s["betweenness_centrality"] for s in services) / len(services), 3
            ) if services else 0.0,
            "system_health": (
                "critical" if any(s["status"] == "critical" for s in services)
                else "degraded" if any(s["status"] == "warning" for s in services)
                else "stable"
            ),
        }

        payload = {
            "services": services,
            "connections": connections,
            "insights": insights,
        }

        # ---- SSE FORMAT ----
        yield f"data: {json.dumps(payload)}\n\n"
        time.sleep(3)
