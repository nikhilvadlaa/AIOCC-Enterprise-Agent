# run_cycle.py
import sys
import os

# Ensure src is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.config import Config
from src.utils.logger import logger

from src.tools.data_fetcher import DataFetcher
from src.tools.slack_notifier import SlackNotifier
from src.tools.email_sender import EmailSender
from src.tools.task_manager import TaskManager
from src.tools.pdf_report import PDFReportGenerator

from src.services.memory_bank import MemoryBank
from src.services.knowledge_base import KnowledgeBase

from src.agents.data_collector_agent import DataCollectorAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.agents.root_cause_agent import RootCauseAgent
from src.agents.decision_maker_agent import DecisionMakerAgent
from src.agents.action_executor_agent import ActionExecutorAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.llm_reasoning_agent import LLMReasoningAgent

def main():
    logger.info("Starting AIOps Control Cycle...")
    
    # Ensure directories exist
    Config.ensure_dirs()

    # Instantiate tools
    logger.info("Initializing tools...")
    fetcher = DataFetcher(
        sales_path=str(Config.SALES_DATA), 
        support_path=str(Config.SUPPORT_DATA), 
        marketing_path=str(Config.MARKETING_DATA)
    )
    slack = SlackNotifier(log_path=str(Config.SLACK_LOGS))
    email = EmailSender()
    tasks = TaskManager(task_file=str(Config.TASKS_FILE))
    pdf = PDFReportGenerator(output_path=str(Config.REPORT_FILE))

    # Services
    logger.info("Initializing services...")
    memory = MemoryBank(path=str(Config.MEMORY_FILE))
    kb = KnowledgeBase(path=str(Config.CHROMA_DB_DIR))

    # Agents
    logger.info("Initializing agents...")
    dc = DataCollectorAgent(fetcher=fetcher)
    an = AnalyticsAgent(lookback_days=14)
    rc = RootCauseAgent(memory_bank=memory, knowledge_base=kb)
    dm = DecisionMakerAgent()
    ae = ActionExecutorAgent(
        slack_notifier=slack, 
        task_manager=tasks, 
        email_sender=email, 
        pdf_generator=pdf, 
        memory_bank=memory
    )
    
    # LLM Agent
    llm = None
    try:
        llm = LLMReasoningAgent(knowledge_base=kb)
        logger.info("LLMReasoningAgent initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not instantiate LLMReasoningAgent: {e}")

    sup = SupervisorAgent(
        data_collector=dc, 
        analytics_agent=an, 
        root_cause_agent=rc, 
        decision_maker=dm, 
        action_executor=ae, 
        memory=memory, 
        llm_agent=llm
    )

    # Run one cycle
    logger.info("Running supervisor cycle...")
    try:
        incident = sup.run_cycle()
        logger.info("--- INCIDENT SAVED ---")
        logger.info(f"Trace ID: {incident['trace_id']}")
        logger.info(f"Insights summary: {incident['insights'].get('summary')}")
        logger.info(f"Plan actions: {[p['action'] for p in incident['plan']]}")
        logger.info(f"Results: {incident['results']}")
    except Exception as e:
        logger.error(f"Error during cycle execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
