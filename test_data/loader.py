import json
from pathlib import Path
from typing import Any, Dict

DATA_FILE = Path(__file__).resolve().parent / "test_data.json"


def load_test_data() -> Dict[str, Any]:
    """
    Loads externalized test data from test_data.json.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Test data file not found at: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
