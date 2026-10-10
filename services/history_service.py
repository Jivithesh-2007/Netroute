"""
Local simulation history persistence service.
"""
import json
import os
import time
from typing import List, Dict, Any


class HistoryService:
    """Manages recording and persisting recent simulation activity logs locally."""

    HISTORY_FILE = "data/history_log.json"

    @classmethod
    def record_simulation(cls, algorithm: str, data_size: int, steps: int, runtime_ms: float, success: bool):
        """Log a completed simulation run to local history file."""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "algorithm": algorithm,
            "data_size": data_size,
            "steps": steps,
            "runtime_ms": round(runtime_ms, 3),
            "success": success
        }

        history = cls.get_history()
        history.insert(0, log_entry)  # Most recent first
        history = history[:50]  # Keep last 50 runs

        os.makedirs(os.path.dirname(cls.HISTORY_FILE), exist_ok=True)
        try:
            with open(cls.HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history log: {e}")

    @classmethod
    def get_history(cls) -> List[Dict[str, Any]]:
        """Load history entries from local storage."""
        if not os.path.exists(cls.HISTORY_FILE):
            return []
        try:
            with open(cls.HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def clear_history(cls):
        """Clear recorded history."""
        if os.path.exists(cls.HISTORY_FILE):
            try:
                os.remove(cls.HISTORY_FILE)
            except Exception:
                pass
