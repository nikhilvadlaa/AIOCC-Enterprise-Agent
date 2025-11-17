# src/services/session_service.py
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

class SessionService:
    """
    Simple file-backed SessionService.

    Session fields:
      - session_id (str)
      - name (str)
      - created_at (iso)
      - updated_at (iso)
      - state: active | paused | finished
      - metadata: dict (arbitrary context, e.g. owner, description)
      - last_trace_id: str (optional)
    """

    def __init__(self, path: str = "sessions.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump([], f, indent=2)

    def _load(self) -> List[Dict[str, Any]]:
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, sessions: List[Dict[str, Any]]):
        with open(self.path, "w") as f:
            json.dump(sessions, f, indent=2)

    def create_session(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        sessions = self._load()
        session = {
            "session_id": str(uuid.uuid4()),
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "state": "active",
            "metadata": metadata or {},
            "last_trace_id": None
        }
        sessions.append(session)
        self._save(sessions)
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        sessions = self._load()
        for s in sessions:
            if s["session_id"] == session_id:
                return s
        return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        return self._load()

    def update_session_state(self, session_id: str, new_state: str) -> Optional[Dict[str, Any]]:
        assert new_state in ("active", "paused", "finished"), "state must be active|paused|finished"
        sessions = self._load()
        updated = None
        for s in sessions:
            if s["session_id"] == session_id:
                s["state"] = new_state
                s["updated_at"] = datetime.utcnow().isoformat()
                updated = s
                break
        if updated is not None:
            self._save(sessions)
        return updated

    def set_last_trace(self, session_id: str, trace_id: str):
        sessions = self._load()
        for s in sessions:
            if s["session_id"] == session_id:
                s["last_trace_id"] = trace_id
                s["updated_at"] = datetime.utcnow().isoformat()
                break
        self._save(sessions)

    def get_active_session(self) -> Optional[Dict[str, Any]]:
        sessions = self._load()
        # return the most recently updated active session, if any
        active = [s for s in sessions if s["state"] == "active"]
        if not active:
            return None
        # sort by updated_at desc
        active = sorted(active, key=lambda x: x["updated_at"], reverse=True)
        return active[0]
