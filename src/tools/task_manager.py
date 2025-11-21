import json
import os
import requests
from datetime import datetime

class TaskManager:
    def __init__(self, task_file="tasks.json"):
        self.task_file = task_file
        self.logger = None
        
        # Trello Config
        self.api_key = os.environ.get("TRELLO_API_KEY")
        self.token = os.environ.get("TRELLO_TOKEN")
        self.board_id = os.environ.get("TRELLO_BOARD_ID")
        self.list_id = os.environ.get("TRELLO_LIST_ID")

        if not os.path.exists(self.task_file):
            with open(self.task_file, "w") as f:
                json.dump([], f)

    def attach_logger(self, logger):
        self.logger = logger

    def create_task(self, title, body, assignee="unassigned", trace_id=None):
        task_id = f"TASK-{int(datetime.utcnow().timestamp())}"
        
        # Try Trello
        if self.api_key and self.token and self.list_id:
            url = "https://api.trello.com/1/cards"
            query = {
                'key': self.api_key,
                'token': self.token,
                'idList': self.list_id,
                'name': title,
                'desc': body
            }
            try:
                response = requests.post(url, params=query)
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get('id', task_id)
                    print(f"[TASK REAL] Created Trello card: {task_id}")
                else:
                    print(f"[TASK ERROR] Trello API: {response.text}")
            except Exception as e:
                print(f"[TASK ERROR] {e}")
        else:
            print(f"[TASK MANAGER] (Mock) New task created: {task_id} - {title}")

        new_task = {
            "id": task_id,
            "title": title,
            "body": body,
            "assignee": assignee,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Write to file
        try:
            with open(self.task_file, "r+") as f:
                try:
                    tasks = json.load(f)
                except json.JSONDecodeError:
                    tasks = []
                tasks.append(new_task)
                f.seek(0)
                json.dump(tasks, f, indent=2)
        except Exception as e:
            print(f"Error writing task logs: {e}")

        if self.logger:
            self.logger.log(
                message=f"Created task {new_task['id']}",
                agent="TaskManager",
                trace_id=trace_id
            )

        return new_task
