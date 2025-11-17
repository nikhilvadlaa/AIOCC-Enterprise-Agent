import json
import os
from datetime import datetime

class TaskManager:
    def __init__(self, task_file="tasks.json"):
        self.task_file = task_file

        if not os.path.exists(self.task_file):
            with open(self.task_file, "w") as f:
                json.dump([], f)

        self.logger = None

    def attach_logger(self, logger):
        self.logger = logger

    def create_task(self, title, body, assignee="unassigned", trace_id=None):
        new_task = {
            "id": f"TASK-{int(datetime.utcnow().timestamp())}",
            "title": title,
            "body": body,
            "assignee": assignee,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Write to file
        with open(self.task_file, "r+") as f:
            tasks = json.load(f)
            tasks.append(new_task)
            f.seek(0)
            json.dump(tasks, f, indent=2)

        print(f"[TASK MANAGER] New task created: {new_task['id']} - {title}")

        if self.logger:
            self.logger.log(
                message=f"Created task {new_task['id']}",
                agent="TaskManager",
                trace_id=trace_id
            )

        return new_task
