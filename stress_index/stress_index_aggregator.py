# SI = (0.4 * CPI) + (0.3 * MPI) + (0.3 * IPI)
# stress_index/stress_index_aggregator.py

from typing import Dict, Any
from utils.logger import get_logger

from stress_index.cpu_pressure_index import compute_cpu_pressure_index
from stress_index.memory_pressure_index import compute_memory_pressure_index
from stress_index.io_pressure_index import compute_io_pressure_index

logger = get_logger(__name__)


def compute_stress_index(metrics: Dict[str, Any]) -> Dict[str, float]:
    """
    Master Stress Index aggregator.
    Produces:
      - cpu_pressure_index
      - memory_pressure_index
      - io_pressure_index
      - stress_index
    """

    cpi = compute_cpu_pressure_index(metrics)
    mpi = compute_memory_pressure_index(metrics)
    ipi = compute_io_pressure_index(metrics)

    # Weighted composite index
    stress_index = (0.4 * cpi) + (0.3 * mpi) + (0.3 * ipi)

    return {
        "cpu_pressure_index": cpi,
        "memory_pressure_index": mpi,
        "io_pressure_index": ipi,
        "stress_index": stress_index,
    }
