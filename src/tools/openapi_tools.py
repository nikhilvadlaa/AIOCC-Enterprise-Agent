# src/tools/openapi_tools.py
import os
import requests
from typing import Dict, Any

BASE = os.getenv("OPENAPI_BASE_URL", os.getenv("AGENT_TOOLS_URL", "http://localhost:8080"))

class OpenAPISlack:
    def __init__(self, base_url: str = None):
        self.base = base_url or BASE

    def post_message(self, channel: str, text: str, attachments: Dict[str, Any]=None, timeout=15):
        url = f"{self.base}/openapi/slack"
        payload = {"channel": channel, "text": text}
        if attachments:
            payload["attachments"] = attachments
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

class OpenAPIEmail:
    def __init__(self, base_url: str = None):
        self.base = base_url or BASE

    def send_email(self, to: str, subject: str, body: str, from_email: str = "noreply@example.com", timeout=15):
        url = f"{self.base}/openapi/email"
        payload = {"to": to, "subject": subject, "body": body, "from_email": from_email}
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

class OpenAPITask:
    def __init__(self, base_url: str = None):
        self.base = base_url or BASE

    def create_task(self, title: str, body: str, assignee: str = None, timeout=15):
        url = f"{self.base}/openapi/task"
        payload = {"title": title, "body": body, "assignee": assignee}
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
