import json
import time
from typing import Dict, Any, List

from utils.time_utils import current_utc_iso
from collectors.node.node_aggregator import collect_node_metrics
from collectors.pod.pod_aggregator import collect_pod_metrics
from config.settings import TARGET_NAMESPACES, WINDOW_SIZE_SECONDS, CLUSTER_ID


def generate_cluster_performance_stream():
    """
    SSE stream for cluster-level performance dashboard
    """

    cpu_history: List[Dict] = []
    mem_history: List[Dict] = []

    while True:
        clusters = []

        # ---- NODE METRICS (cluster-wide) ----
        node_metrics = collect_node_metrics(0, WINDOW_SIZE_SECONDS)
        node = list(node_metrics.values())[0] if node_metrics else {}

        # ---- POD METRICS (cluster-wide count) ----
        total_pods = 0
        for ns in TARGET_NAMESPACES:
            pod_map = collect_pod_metrics(ns, WINDOW_SIZE_SECONDS)
            total_pods += len(pod_map)

        now_label = current_utc_iso()[11:16]  # HH:MM

        cpu_util = node.get("node_cpu_usage_percent", 0.0)
        mem_used = node.get("node_memory_usage_mb", 0.0)
        mem_total = 16.0  # safe fallback (can be auto later)

        cpu_history.append({ "time": now_label, "value": round(cpu_util, 2) })
        mem_history.append({ "time": now_label, "value": round(mem_used, 2) })

        cpu_history[:] = cpu_history[-7:]
        mem_history[:] = mem_history[-7:]

        clusters.append({
            "id": CLUSTER_ID,
            "name": CLUSTER_ID.replace("-", " ").title(),
            "totalNodes": 1,
            "totalPods": total_pods,
            "totalCpu": node.get("node_cpu_cores", 0),
            "totalMemory": round(mem_total, 1),

            "cpu": {
                "utilization": round(cpu_util, 2),
                "speed": 0.0,
                "cores": node.get("node_cpu_cores", 0),
                "threads": node.get("node_cpu_threads", 0),
                "history": cpu_history,
            },

            "memory": {
                "used": round(mem_used, 2),
                "total": round(mem_total, 2),
                "percentage": round((mem_used / mem_total) * 100, 2) if mem_total else 0,
                "cached": 0.0,
                "available": round(mem_total - mem_used, 2),
                "history": mem_history,
            },

            "disk": {
                "activeTime": 0,
                "readSpeed": node.get("node_disk_read_iops", 0.0),
                "writeSpeed": node.get("node_disk_write_iops", 0.0),
                "totalCapacity": 0,
                "used": 0,
            },

            "network": {
                "send": node.get("node_network_tx_kbps", 0.0),
                "receive": node.get("node_network_rx_kbps", 0.0),
                "connections": 0,
            },

            "systemInfo": {
                "uptime": "unknown",
                "processes": total_pods,
                "threads": 0,
                "handles": 0,
            },
        })

        yield f"data: {json.dumps({ 'clusters': clusters })}\n\n"
        time.sleep(2)
