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

    def run_step_by_step(self):
        """
        Generator that yields the current state of the incident resolution process.
        """
        trace_id = str(uuid.uuid4())
        start = datetime.utcnow().isoformat()
        yield {"step": "start", "trace_id": trace_id, "status": "Started"}

        datasets = self.dc.run()
        yield {"step": "data_collection", "data": datasets, "status": "Data Collected"}

        insights = self.an.analyze(datasets)
        yield {"step": "analytics", "insights": insights, "status": "Insights Generated"}

        reasons = self.rc.correlate(insights, datasets)
        yield {"step": "root_cause", "reasons": reasons, "status": "Root Cause Identified"}

        plan = self.dm.make_plan(reasons)
        yield {"step": "initial_plan", "plan": plan, "status": "Initial Plan Created"}

        # Refine plan with LLM if available
        if self.llm and plan:
            try:
                refined_plan = self.llm.refine_plan(plan, insights, reasons)
                if refined_plan:
                    plan = refined_plan
                    yield {"step": "refined_plan", "plan": plan, "status": "Plan Refined by LLM"}
            except Exception as e:
                print(f"[SUPERVISOR] LLM refinement failed: {e}")
                yield {"step": "refined_plan_error", "error": str(e), "status": "LLM Refinement Failed"}

        # Return the final plan for approval (handled by UI)
        yield {"step": "approval_required", "plan": plan, "trace_id": trace_id, "start_time": start, "insights": insights, "reasons": reasons, "status": "Waiting for Approval"}

    def execute_plan(self, plan, trace_id, start_time, insights, reasons):
        """
        Executes the approved plan and records the incident.
        """
        results = []
        if plan:
            results = self.exec.execute(plan, trace_id=trace_id)

        end = datetime.utcnow().isoformat()
        incident = {
            'type': 'incident',
            'trace_id': trace_id,
            'start': start_time,
            'end': end,
            'insights': insights,
            'reasons': reasons,
            'plan': plan,
            'results': results
        }
        self.memory.add_event(incident)
        
        # Add to knowledge base if LLM agent has it
        if self.llm and self.llm.knowledge_base:
            summary = insights.get('summary', 'Incident')
            self.llm.knowledge_base.add_incident(trace_id, summary, results, reasons[0] if reasons else {})

        return incident
