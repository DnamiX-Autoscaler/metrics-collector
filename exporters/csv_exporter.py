# exporters/csv_exporter.py

import csv
import os
from typing import Dict, Any, List
from utils.logger import get_logger
from processors.dataset_row_builder import DATASET_COLUMNS

logger = get_logger(__name__)


def append_row_to_csv(file_path: str, row: Dict[str, Any]) -> None:
    """
    Append a single dataset row to CSV.
    If file doesn't exist, write header first.
    """

    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DATASET_COLUMNS)

        if not file_exists:
            writer.writeheader()

        # Ensure only known columns are written
        filtered_row = {col: row.get(col, "") for col in DATASET_COLUMNS}
        writer.writerow(filtered_row)

    logger.info("Appended row to CSV: %s", file_path)


def write_rows_to_csv(file_path: str, rows: List[Dict[str, Any]]) -> None:
    """
    Write multiple rows to CSV (overwrite existing).
    """

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DATASET_COLUMNS)
        writer.writeheader()

        for row in rows:
            filtered_row = {col: row.get(col, "") for col in DATASET_COLUMNS}
            writer.writerow(filtered_row)

    logger.info("Wrote %d rows to CSV: %s", len(rows), file_path)
