import streamlit as st
import sys
import os
import json
import pandas as pd
import plotly.express as px
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

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

st.set_page_config(page_title="Enterprise AIOps Control Center", layout="wide", page_icon="🤖")

# Custom CSS for "Top 3 Winner" look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        background-color: #00d26a;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00b359;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Enterprise AIOps Control Center")

# Sidebar
st.sidebar.header("System Status")
st.sidebar.success("System Online")
st.sidebar.info("Agents: Active")

# Initialize System (Cached)
@st.cache_resource
def init_system():
    base = os.path.join(os.path.dirname(__file__), "data")
    sales = os.path.join(base, "sales.csv")
    support = os.path.join(base, "support.csv")
    marketing = os.path.join(base, "marketing.csv")

    fetcher = DataFetcher(sales_path=sales, support_path=support, marketing_path=marketing)
    slack = SlackNotifier(log_path="slack_logs.json")
    email = EmailSender()
    tasks = TaskManager(task_file="tasks.json")
    pdf = PDFReportGenerator(output_path="report.pdf")
    memory = MemoryBank(path="memory.json")
    kb = KnowledgeBase(path="data/chroma_db")

    dc = DataCollectorAgent(fetcher=fetcher)
    an = AnalyticsAgent(lookback_days=14)
    rc = RootCauseAgent(memory_bank=memory)
    dm = DecisionMakerAgent()
    ae = ActionExecutorAgent(slack_notifier=slack, task_manager=tasks, email_sender=email, pdf_generator=pdf, memory_bank=memory)
    
    llm = None
    try:
        llm = LLMReasoningAgent(knowledge_base=kb)
    except Exception as e:
        st.warning(f"LLM Agent not available: {e}")

    sup = SupervisorAgent(data_collector=dc, analytics_agent=an, root_cause_agent=rc, decision_maker=dm, action_executor=ae, memory=memory, llm_agent=llm)
    return sup, kb

sup, kb = init_system()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "⚡ Live Operations", "🧠 Knowledge Base"])

with tab1:
    st.header("System Health & Metrics")
    # Mock metrics for visual appeal (in real app, pull from analytics agent)
    col1, col2, col3 = st.columns(3)
    col1.metric("System Uptime", "99.98%", "+0.02%")
    col2.metric("Active Incidents", "0", "-1")
    col3.metric("MTTR (Avg)", "12m", "-2m")
    
    # Chart
    chart_data = pd.DataFrame({
        'Time': pd.date_range(start='2024-01-01', periods=24, freq='H'),
        'Latency (ms)': [x * 10 + 50 for x in range(24)]
    })
    fig = px.line(chart_data, x='Time', y='Latency (ms)', title='System Latency (24h)')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Live Incident Response")
    
    if "incident_state" not in st.session_state:
        st.session_state.incident_state = None
    
    if st.button("🚀 Start Monitoring Cycle"):
        st.session_state.logs = []
        st.session_state.incident_state = "running"
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.container()
        
        step_gen = sup.run_step_by_step()
        
        for step_data in step_gen:
            step_name = step_data['step']
            status = step_data['status']
            
            status_text.text(f"Status: {status}...")
            st.session_state.logs.append(f"[{time.strftime('%H:%M:%S')}] {status}")
            
            # Update logs
            with log_container:
                for log in st.session_state.logs:
                    st.text(log)
            
            if step_name == "approval_required":
                st.session_state.pending_plan = step_data['plan']
                st.session_state.trace_id = step_data['trace_id']
                st.session_state.start_time = step_data['start_time']
                st.session_state.insights = step_data['insights']
                st.session_state.reasons = step_data['reasons']
                st.session_state.incident_state = "waiting_approval"
                progress_bar.progress(80)
                break
                
            time.sleep(1) # Simulate processing time for visual effect
            progress_bar.progress(progress_bar.value + 15)

    if st.session_state.incident_state == "waiting_approval":
        st.warning("⚠️ Approval Required for Remediation Plan")
        
        with st.expander("View Insights & Root Cause", expanded=True):
            st.json(st.session_state.insights)
            st.json(st.session_state.reasons)
            
        st.subheader("Proposed Remediation Plan")
        
        # Editable Plan
        plan_str = json.dumps(st.session_state.pending_plan, indent=2)
        edited_plan_str = st.text_area("Edit Plan JSON", plan_str, height=300)
        
        col1, col2 = st.columns(2)
        if col1.button("✅ Approve & Execute"):
            try:
                final_plan = json.loads(edited_plan_str)
                with st.spinner("Executing Plan..."):
                    result = sup.execute_plan(
                        final_plan, 
                        st.session_state.trace_id, 
                        st.session_state.start_time, 
                        st.session_state.insights, 
                        st.session_state.reasons
                    )
                st.success("Plan Executed Successfully!")
                st.json(result)
                st.session_state.incident_state = "completed"
            except json.JSONDecodeError:
                st.error("Invalid JSON format in plan.")
                
        if col2.button("❌ Reject"):
            st.error("Plan Rejected. Incident logged as unresolved.")
            st.session_state.incident_state = "rejected"

with tab3:
    st.header("🧠 Knowledge Base (RAG)")
    query = st.text_input("Search past incidents...")
    if query:
        results = kb.search_similar(query)
        st.write(results)
