# src/agents/supervisor_agent.py
"""
SupervisorAgent
- Orchestrates the entire detection -> root-cause -> decision -> execution workflow
- Adds tracing (simple trace_id) and stores the incident in memory
"""

import uuid
from datetime import datetime

class SupervisorAgent:
    def __init__(self, data_collector, analytics_agent, root_cause_agent, decision_maker, action_executor, memory, llm_agent=None):
        self.dc = data_collector
        self.an = analytics_agent
        self.rc = root_cause_agent
        self.dm = decision_maker
        self.exec = action_executor
        self.memory = memory
        self.llm = llm_agent

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
        print(f"[SUPERVISOR] Initial Plan: {[p['action'] for p in plan]}")

        # Refine plan with LLM if available
        if self.llm and plan:
            print("[SUPERVISOR] Refining plan with LLM...")
            try:
                refined_plan = self.llm.refine_plan(plan, insights, reasons)
                if refined_plan:
                    plan = refined_plan
                    print(f"[SUPERVISOR] Refined Plan: {[p.get('action') for p in plan]}")
            except Exception as e:
                print(f"[SUPERVISOR] LLM refinement failed, using initial plan. Error: {e}")

        results = []
        if plan:
            results = self.exec.execute(plan, trace_id=trace_id)

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
