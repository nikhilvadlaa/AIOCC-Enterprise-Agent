# src/agents/action_executor_agent.py
"""
ActionExecutorAgent — updated to prefer OpenAPI tools
If OPENAPI_BASE_URL is set and the agent_tools API is reachable, it will use OpenAPI.
Otherwise falls back to existing local tools (SlackNotifier, TaskManager, EmailSender, PDFReportGenerator).
"""

import os
from typing import List, Dict, Any, Optional

from src.config import Config
from src.utils.logger import logger

OPENAPI_BASE = os.getenv("OPENAPI_BASE_URL", os.getenv("AGENT_TOOLS_URL", None))

# Attempt to import OpenAPI wrapper
try:
    from src.tools.openapi_tools import OpenAPISlack, OpenAPIEmail, OpenAPITask
    HAVE_OPENAPI = True
except Exception:
    HAVE_OPENAPI = False

class ActionExecutorAgent:
    def __init__(
        self, 
        slack_notifier: Any = None, 
        task_manager: Any = None, 
        email_sender: Any = None, 
        pdf_generator: Any = None, 
        memory_bank: Any = None
    ):
        # keep fallbacks
        self.slack_local = slack_notifier
        self.task_local = task_manager
        self.email_local = email_sender
        self.pdf = pdf_generator
        self.memory = memory_bank

        # Initialize OpenAPI clients if available
        self.open_slack = None
        self.open_email = None
        self.open_task = None
        if HAVE_OPENAPI and OPENAPI_BASE:
            try:
                self.open_slack = OpenAPISlack(base_url=OPENAPI_BASE)
                self.open_email = OpenAPIEmail(base_url=OPENAPI_BASE)
                self.open_task = OpenAPITask(base_url=OPENAPI_BASE)
                self._using_openapi = True
                logger.info("ActionExecutorAgent using OpenAPI tools.")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAPI tools: {e}")
                self._using_openapi = False
        else:
            self._using_openapi = False

    def _post_slack(self, channel: str, message: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        # prefer openapi
        if self._using_openapi and self.open_slack:
            return self.open_slack.post_message(channel=channel, text=message)
        if self.slack_local:
            return self.slack_local.post_message(channel, message, trace_id=trace_id)
        return {"ok": False, "error": "No slack tool available"}

    def _send_approval(self, channel: str, message: str, action_id: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        # prefer openapi if available (assuming it supports approval)
        # For now, we'll stick to local implementation for the demo
        if self.slack_local:
            return self.slack_local.send_approval_request(channel, message, action_id, trace_id=trace_id)
        return {"ok": False, "error": "No slack tool available for approval"}

    def _create_task(self, title: str, body: str, assignee: Optional[str] = None, trace_id: Optional[str] = None) -> Any:
        if self._using_openapi and self.open_task:
            return self.open_task.create_task(title=title, body=body, assignee=assignee)
        if self.task_local:
            return self.task_local.create_task(title=title, body=body, assignee=assignee, trace_id=trace_id)
        return {"ok": False, "error": "No task tool available"}

    def _send_email(self, to: str, subject: str, body: str, from_email: str = "noreply@example.com", trace_id: Optional[str] = None) -> Dict[str, Any]:
        if self._using_openapi and self.open_email:
            return self.open_email.send_email(to=to, subject=subject, body=body, from_email=from_email)
        if self.email_local:
            return self.email_local.send_email(to=to, subject=subject, body=body, trace_id=trace_id)
        return {"ok": False, "error": "No email tool available"}

    def execute_action(self, item: Dict, trace_id: Optional[str] = None) -> Dict[str, Any]:
        action = item['action']
        owner = item.get('owner', 'unassigned')

        summary = {'action': action, 'owner': owner, 'status': 'pending'}

        if action in ['pause_campaign', 'audit_campaign', 'open_bug', 'create_postmortem']:
            task = self._create_task(title=f"Action: {action}", body=item.get('note',''), assignee=owner, trace_id=trace_id)
            # openapi returns different shape; normalize
            if isinstance(task, dict) and task.get('ok') and task.get('task'):
                task_obj = task['task']
            else:
                task_obj = task.get('card') if isinstance(task, dict) else task
            self._post_slack(channel=owner or "ops", message=f"[AIOCC] Task created for {action}: {task_obj.get('id') if task_obj else 'UNKNOWN'}", trace_id=trace_id)
            summary.update({'status':'task_created', 'task': task_obj})

        elif action == 'human_investigate':
            email_res = self._send_email(to=f"{owner}@example.com", subject="AIOCC Action Required", body=item.get('note',''))
            self._post_slack(channel="ops", message=f"[AIOCC] Manual triage requested. Email sent to {owner}@example.com", trace_id=trace_id)
            summary.update({'status':'email_sent', 'email': email_res})

        elif any(risk in action.lower() for risk in ['restart', 'reboot', 'shutdown', 'delete', 'rollback']):
            # High-risk action: Request Approval
            approval_res = self._send_approval(
                channel="ops", 
                message=f"⚠️ *Approval Required*: Action `{action}` requested by {owner}.\nReason: {item.get('reason', 'No reason provided')}",
                action_id=f"{action}_{trace_id or 'no_trace'}",
                trace_id=trace_id
            )
            summary.update({'status': 'approval_requested', 'approval': approval_res})

        elif action in ['Scale Up Database', 'Clear Redis Cache']:
            # Demo actions
            self._post_slack(channel="ops", message=f"[AIOCC] Executing demo action: {action}", trace_id=trace_id)
            summary.update({'status': 'executed', 'details': 'Simulated execution for demo'})

        else:
            self._post_slack(channel="ops", message=f"[AIOCC] Unknown action: {action}", trace_id=trace_id)
            summary.update({'status':'unknown_action'})

        mem_event = {"type":"action_executed", "action": item, "summary": summary}
        if self.memory:
            self.memory.add_event(mem_event)

        logger.info(f"Executed action {action} (trace_id={trace_id})")

        return summary

    def execute(self, plan: List[Dict], trace_id: Optional[str] = None) -> List[Dict]:
        results = []
        for item in plan:
            res = self.execute_action(item, trace_id=trace_id)
            results.append(res)

        # Generate PDF report (best-effort)
        try:
            reasons = [p.get('reason') for p in plan]
            insights = {"summary":"Auto-generated"}
            if self.pdf:
                # pass trace_id if supported
                try:
                    self.pdf.generate_report(insights=insights, reasons=reasons, plan=plan, result=results, trace_id=trace_id)
                except TypeError:
                    self.pdf.generate_report(insights=insights, reasons=reasons, plan=plan, result=results)
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")

        return results
