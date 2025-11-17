import json
import os
from datetime import datetime
import tempfile
import shutil
import numpy as np

class MemoryBank:
    def __init__(self, path='memory.json'):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf8') as f:
                json.dump([], f)

    def _to_json_safe(self, obj):
        if isinstance(obj, dict):
            return {k: self._to_json_safe(v) for k, v in obj.items()}

        if isinstance(obj, (list, tuple)):
            return [self._to_json_safe(i) for i in obj]

        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)

        if isinstance(obj, (np.integer,)):
            return int(obj)

        if isinstance(obj, (np.floating,)):
            return float(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        return obj

    def _safe_load(self):
        if not os.path.exists(self.path):
            return []

        try:
            with open(self.path, 'r', encoding='utf8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            corrupt_backup = f"{self.path}.corrupt.{ts}"
            shutil.copy(self.path, corrupt_backup)
            with open(self.path, 'w', encoding='utf8') as f:
                json.dump([], f)
            print(f"[MemoryBank] WARNING: memory.json was corrupted; backed up to {corrupt_backup}. Resetting.")
            return []
        except Exception as e:
            raise

    def _atomic_write(self, data):
        dirn = os.path.dirname(os.path.abspath(self.path))
        with tempfile.NamedTemporaryFile('w', delete=False, dir=dirn, encoding='utf8') as tf:
            json.dump(data, tf, indent=2)
            tmpname = tf.name
        shutil.move(tmpname, self.path)

    def add_event(self, event):
        data = self._safe_load()
        safe_event = self._to_json_safe(event)
        safe_event.setdefault("timestamp", datetime.utcnow().isoformat())
        data.append(safe_event)
        self._atomic_write(data)
        return safe_event

    def query_recent(self, n=10):
        data = self._safe_load()
        return data[-n:]

    def find_by_type(self, event_type):
        data = self._safe_load()
        return [d for d in data if d.get('type') == event_type]

    def set_kpi_baseline(self, kpi_name: str, value: float):
        return self.add_event({"type": "kpi_baseline", "kpi": kpi_name, "value": float(value)})

    def get_latest_kpi(self, kpi_name: str):
        data = self._safe_load()
        for d in reversed(data):
            if d.get('type') == 'kpi_baseline' and d.get('kpi') == kpi_name:
                return d.get('value')
        return None
