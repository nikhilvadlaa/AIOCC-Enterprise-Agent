import json
from datetime import datetime
import os

class SlackNotifier:
    def __init__(self, log_path="slack_logs.json"):
        self.log_path = log_path
        self.logger = None
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                json.dump([], f)

    def attach_logger(self, logger):
        self.logger = logger

    def post_message(self, channel, message, trace_id=None):
        if self.logger:
            self.logger.log(
                message=f"Slack post to #{channel}: {message}",
                level="INFO",
                agent="SlackNotifier",
                trace_id=trace_id if 'trace_id' in locals() else None
         )

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "channel": channel,
            "message": message
        }

        with open(self.log_path, "r+") as f:
            logs = json.load(f)
            logs.append(log_entry)
            f.seek(0)
            json.dump(logs, f, indent=2)

        print(f"[SLACK MOCK] #{channel}: {message}")
