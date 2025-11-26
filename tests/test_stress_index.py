# tests/test_stress_index.py

from stress_index.cpu_pressure_index import compute_cpu_pressure_index
from stress_index.memory_pressure_index import compute_memory_pressure_index
from stress_index.io_pressure_index import compute_io_pressure_index
from stress_index.stress_index_aggregator import compute_stress_index


def test_cpu_pressure_index_basic():
    metrics = {
        "pod_cpu_usage_percent_p95": 80.0,
        "pod_cpu_limit_percent": 100.0,
    }
    cpi = compute_cpu_pressure_index(metrics)
    assert cpi == 0.8


def test_memory_pressure_index_basic():
    metrics = {
        "pod_memory_usage_mb_p95": 400.0,
        "pod_memory_limit_percent": 800.0,
    }
    mpi = compute_memory_pressure_index(metrics)
    assert mpi == 0.5


def test_io_pressure_index_basic():
    metrics = {
        "node_disk_read_iops": 100.0,
        "node_disk_write_iops": 50.0,
        "node_cpu_usage_percent": 50.0,
    }
    ipi = compute_io_pressure_index(metrics)
    # (100+50)/(50+1) = 150/51 ≈ 2.94
    assert 2.8 < ipi < 3.1


def test_stress_index_aggregator():
    metrics = {
        "pod_cpu_usage_percent_p95": 90.0,
        "pod_cpu_limit_percent": 100.0,   # cpi = 0.9
        "pod_memory_usage_mb_p95": 300.0,
        "pod_memory_limit_percent": 600.0,  # mpi = 0.5
        "node_disk_read_iops": 100.0,
        "node_disk_write_iops": 100.0,
        "node_cpu_usage_percent": 50.0,  # ipi ≈ 200 / 51 ≈ 3.92
    }

    stress = compute_stress_index(metrics)
    cpi = stress["cpu_pressure_index"]
    mpi = stress["memory_pressure_index"]
    ipi = stress["io_pressure_index"]
    si = stress["stress_index"]

    # Check individual components
    assert abs(cpi - 0.9) < 1e-6
    assert abs(mpi - 0.5) < 1e-6
    assert 3.5 < ipi < 4.5

    # Check weighted composite
    expected_si = 0.4 * cpi + 0.3 * mpi + 0.3 * ipi
    assert abs(si - expected_si) < 1e-6
