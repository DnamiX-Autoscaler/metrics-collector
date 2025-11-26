# IPI = (node_disk_read_iops + node_disk_write_iops) / (node_cpu_usage_percent + 1)
# stress_index/io_pressure_index.py

from typing import Dict

def compute_io_pressure_index(metrics: Dict[str, float]) -> float:
    """
    IO Pressure Index =
        (node_disk_read_iops + node_disk_write_iops) / (node_cpu_usage_percent + 1)
    """

    read_iops = metrics.get("node_disk_read_iops", 0.0)
    write_iops = metrics.get("node_disk_write_iops", 0.0)
    node_cpu = metrics.get("node_cpu_usage_percent", 0.0)

    return (read_iops + write_iops) / (node_cpu + 1)
