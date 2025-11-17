# run_cycle_sessions.py
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.tools.data_fetcher import DataFetcher
from src.tools.slack_notifier import SlackNotifier
from src.tools.email_sender import EmailSender
from src.tools.task_manager import TaskManager
from src.tools.pdf_report import PDFReportGenerator

from src.services.memory_bank import MemoryBank
from src.services.session_service import SessionService

from src.agents.data_collector_agent import DataCollectorAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.agents.root_cause_agent import RootCauseAgent
from src.agents.decision_maker_agent import DecisionMakerAgent
from src.agents.action_executor_agent import ActionExecutorAgent
from src.agents.supervisor_with_session_agent import SupervisorWithSession

def main():
    base = os.path.join(os.path.dirname(__file__), "data")
    sales = os.path.join(base, "sales.csv")
    support = os.path.join(base, "support.csv")
    marketing = os.path.join(base, "marketing.csv")

    # Tools
    fetcher = DataFetcher(sales_path=sales, support_path=support, marketing_path=marketing)
    slack = SlackNotifier(log_path="slack_logs.json")
    email = EmailSender()
    tasks = TaskManager(task_file="tasks.json")
    pdf = PDFReportGenerator(output_path="report.pdf")

    # Services
    memory = MemoryBank(path="memory.json")
    sessions = SessionService(path="sessions.json")

    # Agents
    dc = DataCollectorAgent(fetcher=fetcher)
    an = AnalyticsAgent(lookback_days=14)
    rc = RootCauseAgent(memory_bank=memory)
    dm = DecisionMakerAgent()
    ae = ActionExecutorAgent(slack_notifier=slack, task_manager=tasks, email_sender=email, pdf_generator=pdf, memory_bank=memory)

    sup = SupervisorWithSession(data_collector=dc, analytics_agent=an, root_cause_agent=rc, decision_maker=dm, action_executor=ae, memory_bank=memory, session_service=sessions)

    # 1) Create a session
    s = sup.create_session(name="AIOCC-demo", metadata={"owner":"you", "env":"dev"})
    sid = s["session_id"]
    print("Created session:", sid)

    # 2) Run one cycle -> should execute
    print("\n=== RUN 1 (should run) ===")
    incident1 = sup.run_cycle(session_id=sid)

    # 3) Pause session
    print("\nPausing session...")
    sup.pause_session(sid)

    # 4) Attempt run -> should be skipped
    print("\n=== RUN 2 (should be skipped because paused) ===")
    res = sup.run_cycle(session_id=sid)
    print("Run 2 result:", res)

    # 5) Resume session
    print("\nResuming session...")
    sup.resume_session(sid)

    # 6) Run again -> should execute
    print("\n=== RUN 3 (should run after resume) ===")
    incident3 = sup.run_cycle(session_id=sid)

    print("\nDemo complete. Inspect sessions.json, memory.json, tasks.json, slack_logs.json")

if __name__ == "__main__":
    main()
