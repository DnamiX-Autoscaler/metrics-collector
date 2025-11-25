# exporters/json_exporter.py

import json
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


def append_row_to_jsonl(file_path: str, row: Dict[str, Any]) -> None:
    """
    Append row as a single line of JSON (JSONL format).
    """

    with open(file_path, mode="a", encoding="utf-8") as f:
        f.write(json.dumps(row))
        f.write("\n")

    logger.info("Appended row to JSONL: %s", file_path)


def write_rows_to_json(file_path: str, rows: List[Dict[str, Any]]) -> None:
    """
    Write list of rows as a JSON array (overwrite).
    """

    with open(file_path, mode="w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    logger.info("Wrote %d rows to JSON: %s", len(rows), file_path)
