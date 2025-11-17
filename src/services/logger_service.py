# src/services/logger_service.py
import json
from datetime import datetime

class LoggerService:
    """
    Writes each log entry as a JSON line in logs.jsonl:
        {"timestamp": "...", "trace_id": "...", "agent": "...", "level": "...", "message": "..."}
    """

    def __init__(self, path="logs.jsonl"):
        self.path = path

    def log(self, message, level="INFO", agent="system", trace_id=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "agent": agent,
            "level": level,
            "message": message
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[{agent}:{level}] {message}")
