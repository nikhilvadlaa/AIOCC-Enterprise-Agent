import json
import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackNotifier:
    def __init__(self, log_path="slack_logs.json"):
        self.log_path = log_path
        self.token = os.environ.get("SLACK_BOT_TOKEN")
        self.client = WebClient(token=self.token) if self.token else None
        self.logger = None
        
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                json.dump([], f)

    def attach_logger(self, logger):
        self.logger = logger

    def post_message(self, channel, message, trace_id=None):
        result = {"ok": False, "message": "Init"}
        
        # Try sending to real Slack if token is present
        if self.client:
            try:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=message
                )
                result = {"ok": True, "ts": response.get("ts"), "channel": channel}
                print(f"[SLACK REAL] Sent to #{channel}: {message}")
            except SlackApiError as e:
                print(f"[SLACK ERROR] {e.response['error']}")
                result = {"ok": False, "error": e.response['error']}
        else:
            print(f"[SLACK MOCK] (No Token) #{channel}: {message}")
            result = {"ok": True, "mock": True}

        # Log internally
        if self.logger:
            self.logger.log(
                message=f"Slack post to #{channel}: {message}",
                level="INFO",
                agent="SlackNotifier",
                trace_id=trace_id if 'trace_id' in locals() else None
            )

        # Persist to local log file
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "channel": channel,
            "message": message,
            "result": result
        }

        try:
            with open(self.log_path, "r+") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
                logs.append(log_entry)
                f.seek(0)
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error writing slack logs: {e}")
            
        return result

    def send_approval_request(self, channel, message, action_id, trace_id=None):
        """
        Sends a message with Approve/Deny buttons.
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": "approve",
                        "action_id": f"approve_{action_id}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Deny",
                            "emoji": True
                        },
                        "style": "danger",
                        "value": "deny",
                        "action_id": f"deny_{action_id}"
                    }
                ]
            }
        ]

        result = {"ok": False, "message": "Init"}
        
        if self.client:
            try:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=message, # Fallback text
                    blocks=blocks
                )
                result = {"ok": True, "ts": response.get("ts"), "channel": channel}
                print(f"[SLACK REAL] Sent Approval Request to #{channel}: {message}")
            except SlackApiError as e:
                print(f"[SLACK ERROR] {e.response['error']}")
                result = {"ok": False, "error": e.response['error']}
        else:
            print(f"[SLACK MOCK] (No Token) Approval Request #{channel}: {message} [Approve] [Deny]")
            result = {"ok": True, "mock": True}

        # Log internally
        if self.logger:
            self.logger.log(
                message=f"Slack approval request to #{channel}: {message}",
                level="INFO",
                agent="SlackNotifier",
                trace_id=trace_id if 'trace_id' in locals() else None
            )
            
        return result
