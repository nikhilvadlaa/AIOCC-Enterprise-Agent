# src/agents/supervisor_with_session_agent.py

import uuid
from datetime import datetime

try:
    from src.agents.supervisor_agent import SupervisorAgent as BaseSupervisor
    USING_BASE = True
except Exception:
    BaseSupervisor = None
    USING_BASE = False


class SupervisorWithSession:
    def __init__(
        self,
        data_collector,
        analytics_agent,
        root_cause_agent,
        decision_maker,
        action_executor,
        memory_bank,
        session_service
    ):
        self.session_service = session_service
        self.memory = memory_bank
        self.logger = None

        # Delegates to your original supervisor
        if USING_BASE:
            self.base = BaseSupervisor(
                data_collector,
                analytics_agent,
                root_cause_agent,
                decision_maker,
                action_executor,
                memory_bank
            )
        else:
            self.base = None
            self.dc = data_collector
            self.analytics = analytics_agent
            self.rc = root_cause_agent
            self.dm = decision_maker
            self.exec = action_executor

    def attach_logger(self, logger):
        self.logger = logger

    def create_session(self, name, metadata=None):
        return self.session_service.create_session(name=name, metadata=metadata or {})

    def pause_session(self, sid):
        return self.session_service.update_session_state(sid, "paused")

    def resume_session(self, sid):
        return self.session_service.update_session_state(sid, "active")

    def finish_session(self, sid):
        return self.session_service.update_session_state(sid, "finished")

    def run_cycle(self, session_id=None):
        # Resolve active session
        if session_id:
            session = self.session_service.get_session(session_id)
        else:
            session = self.session_service.get_active_session()

        if not session:
            session = self.create_session("default-session")

        sid = session["session_id"]

        # Check paused
        if session["state"] == "paused":
            print(f"[SUPERVISOR+SESSION] Session {sid} paused — skipping cycle.")
            if self.logger:
                self.logger.log(
                    message=f"Session {sid} paused; cycle skipped.",
                    agent="SupervisorWithSession",
                    trace_id=None
                )
            return {"skipped": True, "reason": "paused", "session": session}

        trace_id = str(uuid.uuid4())

        if self.logger:
            self.logger.log(
                message=f"Session {sid} starting cycle",
                agent="SupervisorWithSession",
                trace_id=trace_id
            )

        # Run underlying supervisor
        if self.base:
            incident = self.base.run_cycle()
        else:
            # Fallback
            start = datetime.utcnow().isoformat()
            datasets = self.dc.run()
            insights = self.analytics.analyze(datasets)
            reasons = self.rc.correlate(insights, datasets)
            plan = self.dm.make_plan(reasons)
            results = self.exec.execute(plan, trace_id=trace_id)

            end = datetime.utcnow().isoformat()

            incident = {
                "type": "incident",
                "trace_id": trace_id,
                "start": start,
                "end": end,
                "insights": insights,
                "reasons": reasons,
                "plan": plan,
                "results": results
            }
            self.memory.add_event(incident)

        # Update session trace
        self.session_service.set_last_trace(sid, incident["trace_id"])

        if self.logger:
            self.logger.log(
                message=f"Cycle complete for session {sid}",
                agent="SupervisorWithSession",
                trace_id=incident["trace_id"]
            )

        print(f"[SUPERVISOR+SESSION] Completed cycle trace_id={incident['trace_id']}")
        return incident
