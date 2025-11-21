# run_cycle.py
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# ensure src is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.tools.data_fetcher import DataFetcher
from src.tools.slack_notifier import SlackNotifier
from src.tools.email_sender import EmailSender
from src.tools.task_manager import TaskManager
from src.tools.pdf_report import PDFReportGenerator

from src.services.memory_bank import MemoryBank

from src.agents.data_collector_agent import DataCollectorAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.agents.root_cause_agent import RootCauseAgent
from src.agents.decision_maker_agent import DecisionMakerAgent
from src.agents.action_executor_agent import ActionExecutorAgent
from src.agents.supervisor_agent import SupervisorAgent

from src.agents.llm_reasoning_agent import LLMReasoningAgent

def main():
    # Paths: adjust if your data is in a different location
    base = os.path.join(os.path.dirname(__file__), "data")
    sales = os.path.join(base, "sales.csv")
    support = os.path.join(base, "support.csv")
    marketing = os.path.join(base, "marketing.csv")

    # Instantiate tools
    fetcher = DataFetcher(sales_path=sales, support_path=support, marketing_path=marketing)
    slack = SlackNotifier(log_path="slack_logs.json")
    email = EmailSender()
    tasks = TaskManager(task_file="tasks.json")
    pdf = PDFReportGenerator(output_path="report.pdf")

    # Services
    memory = MemoryBank(path="memory.json")

    # Agents
    dc = DataCollectorAgent(fetcher=fetcher)
    an = AnalyticsAgent(lookback_days=14)
    rc = RootCauseAgent(memory_bank=memory)
    dm = DecisionMakerAgent()
    ae = ActionExecutorAgent(slack_notifier=slack, task_manager=tasks, email_sender=email, pdf_generator=pdf, memory_bank=memory)
    
    # LLM Agent (optional, requires Vertex AI)
    llm = None
    try:
        llm = LLMReasoningAgent()
    except Exception as e:
        print(f"Warning: Could not instantiate LLMReasoningAgent: {e}")

    sup = SupervisorAgent(data_collector=dc, analytics_agent=an, root_cause_agent=rc, decision_maker=dm, action_executor=ae, memory=memory, llm_agent=llm)

    # Run one cycle
    incident = sup.run_cycle()
    print("\n--- INCIDENT SAVED ---")
    print(f"Trace ID: {incident['trace_id']}")
    print(f"Insights summary: {incident['insights'].get('summary')}")
    print(f"Plan actions: {[p['action'] for p in incident['plan']]}")
    print(f"Results: {incident['results']}")

if __name__ == "__main__":
    main()
