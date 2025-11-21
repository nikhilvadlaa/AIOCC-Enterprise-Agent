# Kaggle Notebook Submission Guide

This guide will help you port your **Enterprise AIOps Control Center** to a Kaggle Notebook.

## 1. Setup on Kaggle
1.  **Create a New Notebook**: Go to Kaggle and click "New Notebook".
2.  **Add Data**:
    *   In the "Data" panel (right side), click "Add Data".
    *   Upload your local `data/` folder (sales.csv, support.csv, marketing.csv, incident_history.json).
    *   *Note: You might need to zip them up first or upload them individually.*
3.  **Add Secrets**:
    *   Go to "Add-ons" -> "Secrets".
    *   Add `SLACK_BOT_TOKEN` and `GOOGLE_CLOUD_PROJECT`.
    *   *Note: For the video/demo, you can skip this if using the Mock mode.*

## 2. The Code (Copy & Paste)
Copy the following code blocks into your notebook cells.

### Cell 1: Imports & Configuration
```python
# Install dependencies
!pip install slack_sdk sendgrid reportlab google-cloud-aiplatform google-cloud-secret-manager

import os
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime

# Configuration
# Try to get secrets from Kaggle, else use placeholders
from kaggle_secrets import UserSecretsClient
try:
    user_secrets = UserSecretsClient()
    SLACK_TOKEN = user_secrets.get_secret("SLACK_BOT_TOKEN")
    PROJECT_ID = user_secrets.get_secret("GOOGLE_CLOUD_PROJECT")
except:
    SLACK_TOKEN = None
    PROJECT_ID = "mock-project"

print("Configuration Loaded.")
```

### Cell 2: Services (Memory & RAG)
```python
class KnowledgeBase:
    def __init__(self, data_path="/kaggle/input/your-dataset/incident_history.json"):
        # Adjust path based on where you uploaded the data
        self.data_path = data_path
        self.incidents = self._load_data()

    def _load_data(self) -> List[Dict]:
        if not os.path.exists(self.data_path):
            # Fallback seed data if file not found
            return [
                {"id": "INC-001", "symptoms": "High latency", "root_cause": "Memory leak", "resolution": "Restart"},
                {"id": "INC-002", "symptoms": "Database timeout", "root_cause": "Connection pool", "resolution": "Increase pool"}
            ]
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except:
            return []

    def search(self, query: str) -> List[Dict]:
        # Simple keyword search
        query_words = set(query.lower().split())
        results = []
        for inc in self.incidents:
            text = (inc.get('symptoms', '') + " " + inc.get('root_cause', '')).lower()
            if any(w in text for w in query_words):
                results.append(inc)
        return results[:2]

class MemoryBank:
    def __init__(self):
        self.events = []
    def add_event(self, event):
        self.events.append(event)
    def get_events(self):
        return self.events
```

### Cell 3: Tools (Slack & Mocking)
```python
class SlackNotifier:
    def __init__(self, token=None):
        self.token = token
    
    def post_message(self, channel, message):
        print(f"[SLACK] #{channel}: {message}")
        return {"ok": True}

    def send_approval_request(self, channel, message, action_id):
        print(f"\n>>> [SLACK INTERACTIVE] #{channel} <<<")
        print(f"MSG: {message}")
        print(f"[BUTTON] Approve {action_id}")
        print(f"[BUTTON] Deny {action_id}")
        print(">>> Waiting for user interaction... (Simulated: APPROVED)")
        return {"ok": True, "status": "approved"}
```

### Cell 4: Agents (The Core Logic)
```python
class DataCollectorAgent:
    def collect(self):
        # Simulate reading data
        return {
            "sales": {"conversion_rate": 0.02},
            "support": {"ticket_volume": 150}, # Spike!
            "marketing": {"ad_spend": 5000}
        }

class AnalyticsAgent:
    def analyze(self, data):
        insights = {}
        if data['support']['ticket_volume'] > 100:
            insights['support_spike'] = True
            insights['summary'] = "High support ticket volume detected."
        return insights

class RootCauseAgent:
    def __init__(self, kb):
        self.kb = kb
    
    def diagnose(self, insights):
        reasons = []
        if insights.get('support_spike'):
            # RAG Search
            past = self.kb.search("support timeout")
            if past:
                reasons.append({
                    "reason": "similar_past_incident",
                    "detail": f"Matches {past[0]['id']}: {past[0]['root_cause']}"
                })
            else:
                reasons.append({"reason": "unknown_spike", "detail": "Needs investigation"})
        return reasons

class ActionExecutorAgent:
    def __init__(self, slack):
        self.slack = slack
    
    def execute(self, plan):
        results = []
        for action in plan:
            if action == 'restart_server':
                # Human in the Loop
                self.slack.send_approval_request("ops", "Restart Required", "act_123")
                print("[ACTION] Restarting Server... DONE")
                results.append("restarted")
            else:
                print(f"[ACTION] Executing {action}")
                results.append(action)
        return results

class SupervisorAgent:
    def run(self):
        print("--- Starting AIOps Cycle ---")
        
        # 1. Collect
        dc = DataCollectorAgent()
        data = dc.collect()
        
        # 2. Analyze
        an = AnalyticsAgent()
        insights = an.analyze(data)
        print(f"[Insights] {insights.get('summary')}")
        
        # 3. Root Cause (RAG)
        kb = KnowledgeBase() # Uses fallback or uploaded data
        rc = RootCauseAgent(kb)
        reasons = rc.diagnose(insights)
        print(f"[Root Cause] {reasons}")
        
        # 4. Plan & Execute
        ae = ActionExecutorAgent(SlackNotifier(SLACK_TOKEN))
        if reasons and reasons[0]['reason'] == 'similar_past_incident':
            print("[Decision] Found known fix. Initiating remediation.")
            ae.execute(['restart_server'])
        else:
            print("[Decision] Unknown cause. Requesting manual triage.")
            ae.execute(['human_investigate'])
            
        print("--- Cycle Complete ---")
```

### Cell 5: Run It!
```python
supervisor = SupervisorAgent()
supervisor.run()
```

## 3. Submission Checklist
1.  [ ] **Public**: Make sure your notebook is set to "Public" if required by the competition.
2.  [ ] **Video Link**: Add a markdown cell at the top with the link to your YouTube video.
3.  [ ] **Description**: Copy your `README.md` content into the first markdown cell of the notebook to explain the project.
