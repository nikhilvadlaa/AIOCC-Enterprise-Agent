# agent_tools_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
import os
import requests
from typing import Optional, Dict, Any

app = FastAPI(title="AIOCC Agent Tools API", version="1.0.0")

# Config via env
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
TRELLO_KEY = os.getenv("TRELLO_KEY", "")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN", "")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID", "")  # default list id to create cards into

# ---------------------------
# Models
# ---------------------------
class SlackPost(BaseModel):
    channel: str = Field(..., description="Slack channel name or id (e.g. '#ops' or 'C12345')")
    text: str = Field(..., description="Message text")
    attachments: Optional[Dict[str, Any]] = None

class EmailSend(BaseModel):
    to: EmailStr
    subject: str
    body: str
    from_email: Optional[EmailStr] = Field(default="noreply@example.com")

class TaskCreate(BaseModel):
    title: str
    body: str
    assignee: Optional[str] = None

# ---------------------------
# Slack endpoint
# ---------------------------
@app.post("/openapi/slack", summary="Post message to Slack (Webhook or API)")
def post_slack(payload: SlackPost):
    # Prefer webhook if configured
    if SLACK_WEBHOOK:
        try:
            data = {"text": payload.text}
            # If user passed a channel override we include it
            if payload.channel:
                data["channel"] = payload.channel
            r = requests.post(SLACK_WEBHOOK, json=data, timeout=15)
            r.raise_for_status()
            return {"ok": True, "method": "webhook", "status_code": r.status_code}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Slack webhook failed: {e}")

    # Else try Slack API token method (chat.postMessage)
    if SLACK_BOT_TOKEN:
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-type": "application/json"}
        body = {"channel": payload.channel, "text": payload.text}
        try:
            r = requests.post("https://slack.com/api/chat.postMessage", json=body, headers=headers, timeout=15)
            r.raise_for_status()
            res = r.json()
            if not res.get("ok"):
                raise Exception(res)
            return {"ok": True, "method": "api", "response": res}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Slack API failed: {e}")

    # Fallback: mock
    return {"ok": True, "method": "mock", "message": f"[MOCK] #{payload.channel}: {payload.text}"}

# ---------------------------
# Email endpoint
# ---------------------------
@app.post("/openapi/email", summary="Send email via SendGrid or SMTP")
def send_email(payload: EmailSend):
    # Try SendGrid
    if SENDGRID_API_KEY:
        headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
        body = {
            "personalizations": [{"to": [{"email": payload.to}], "subject": payload.subject}],
            "from": {"email": payload.from_email},
            "content": [{"type": "text/plain", "value": payload.body}]
        }
        try:
            r = requests.post("https://api.sendgrid.com/v3/mail/send", json=body, headers=headers, timeout=15)
            r.raise_for_status()
            return {"ok": True, "method": "sendgrid", "status_code": r.status_code}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SendGrid failed: {e}")

    # SMTP fallback
    if SMTP_HOST and SMTP_USER:
        import smtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = payload.subject
        msg["From"] = payload.from_email
        msg["To"] = payload.to
        msg.set_content(payload.body)
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            return {"ok": True, "method": "smtp"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SMTP failed: {e}")

    # Mock
    return {"ok": True, "method": "mock", "message": f"[MOCK EMAIL] To: {payload.to}, Subject: {payload.subject}"}

# ---------------------------
# Task endpoint (Trello example)
# ---------------------------
@app.post("/openapi/task", summary="Create a task (Trello card) or mock")
def create_task(payload: TaskCreate):
    # Trello
    if TRELLO_KEY and TRELLO_TOKEN and TRELLO_LIST_ID:
        url = "https://api.trello.com/1/cards"
        params = {
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN,
            "idList": TRELLO_LIST_ID,
            "name": payload.title,
            "desc": payload.body
        }
        try:
            r = requests.post(url, params=params, timeout=15)
            r.raise_for_status()
            return {"ok": True, "method": "trello", "card": r.json()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Trello failed: {e}")

    # Mock
    # Return a fake task id but real-looking structure
    fake = {"id": f"TASK-MOCK-{os.urandom(4).hex()}", "name": payload.title, "desc": payload.body}
    return {"ok": True, "method": "mock", "task": fake}
