# src/agents/supervisor_agent.py
"""
SupervisorAgent
- Orchestrates the entire detection -> root-cause -> decision -> execution workflow
- Adds tracing (simple trace_id) and stores the incident in memory
"""

import uuid
from datetime import datetime

class SupervisorAgent:
    def __init__(self, data_collector, analytics_agent, root_cause_agent, decision_maker, action_executor, memory):
        self.dc = data_collector
        self.an = analytics_agent
        self.rc = root_cause_agent
        self.dm = decision_maker
        self.exec = action_executor
        self.memory = memory

    def run_cycle(self):
        trace_id = str(uuid.uuid4())
        start = datetime.utcnow().isoformat()
        print(f"[SUPERVISOR] Starting cycle trace_id={trace_id} at {start}")

        datasets = self.dc.run()
        insights = self.an.analyze(datasets)
        print(f"[SUPERVISOR] Insights: {insights.get('summary')}")

        reasons = self.rc.correlate(insights, datasets)
        print(f"[SUPERVISOR] Reasons: {[r['reason'] for r in reasons]}")

        plan = self.dm.make_plan(reasons)
        print(f"[SUPERVISOR] Plan: {[p['action'] for p in plan]}")

        results = []
        if plan:
            results = self.exec.execute(plan)

        end = datetime.utcnow().isoformat()
        incident = {
            'type': 'incident',
            'trace_id': trace_id,
            'start': start,
            'end': end,
            'insights': insights,
            'reasons': reasons,
            'plan': plan,
            'results': results
        }
        self.memory.add_event(incident)

        print(f"[SUPERVISOR] Cycle complete trace_id={trace_id}; actions_executed={len(results)}")
        return incident
