# 🤖 AIOCC — Enterprise AIOps Control Center

> **Track:** Enterprise Agents  
> **Tagline:** An autonomous, self-healing AIOps co-pilot that detects incidents, finds root causes, and executes remediation — powered by Gemini.

---

## 1. 🚨 Problem

Modern SRE / Ops teams are drowning in:

- **Alert fatigue** from multiple tools (monitoring, tickets, logs).
- **Context switching** between dashboards to connect metrics, logs and incidents.
- **Slow, manual remediation** for common patterns like memory leaks, CPU spikes, or bad deploys.

This inflates **MTTR (Mean Time To Resolution)** and burns out engineers. Most incidents follow **repeatable patterns**, but humans still do the investigation and fixes manually.

---

## 2. 💡 Solution — Enterprise AIOps Control Center (AIOCC)

**AIOCC** is a multi-agent AIOps system that:

1. **Continuously ingests** synthetic observability data (sales, support, marketing as “signals” for demand / load).
2. **Detects anomalies** and correlates signals into incidents.
3. **Finds likely root causes** across the datasets.
4. **Plans remediation** steps using a decision agent + Gemini.
5. **Executes remediation actions** via tools (Slack, email, ticketing, PDF report).
6. **Stores incidents in memory** to improve future recommendations (RAG on past incidents).

Instead of “just alerts”, AIOCC behaves like a **self-healing runbook executor** that can:

- Explain: *“What’s going on?”*  
- Justify: *“Why did this happen?”*  
- Act: *“What should we do now?”*

---

## 3. 🌉 Core Concept & Value (for judges)

- **Enterprise fit:** Mirrors a realistic AIOps workflow: signal ingestion → anomaly detection → root cause → action.
- **Agents are central:** Each step is handled by a specialized agent orchestrated by a supervisor.
- **Value to SREs:**
  - Reduces **MTTR** with automated investigation + remediation.
  - Reduces **alert fatigue** by aggregating signals into meaningful incidents.
  - Creates a **knowledge base of incidents** that can be reused (RAG).

---

## 4. 🧠 Agent Architecture

### 4.1 Multi-Agent System

Core agents (in `src/agents/`):

- **DataCollectorAgent** — pulls fresh CSV data via `DataFetcher` (simulating observability feeds).
- **AnalyticsAgent** — computes KPIs & detects anomalies (e.g., spikes, drops).
- **RootCauseAgent** — correlates anomalies across datasets to propose root causes.
- **DecisionMakerAgent** — turns root causes into an initial remediation plan.
- **LLMReasoningAgent** — uses **Gemini** for:
  - Refining the remediation plan.
  - Explaining root cause and impact in natural language.
  - Using the **KnowledgeBase** for RAG on past incidents.
- **ActionExecutorAgent** — executes actions through tools:
  - Slack notifications
  - Email
  - Ticket/task creation
  - PDF incident report
- **SupervisorAgent** — orchestrates end-to-end flow and logs everything.
- **SupervisorWithSession** — wraps Supervisor with **session management** (long-running / pause-resume).

Support services (in `src/services/`):

- `MemoryBank` — long-term memory of incidents and KPI baselines.
- `SessionService` — file-backed sessions with pause / resume / last trace.
- `KnowledgeBase` — simple vector-like store over incidents for RAG-style retrieval.

Tools (in `src/tools/`):

- `DataFetcher` — loads CSVs from `data/`.
- `SlackNotifier` / `EmailSender` — send alerts.
- `TaskManager` — creates tasks / tickets.
- `PDFReportGenerator` — exports incident reports.
- `openapi_tools.py` — wraps an **Agent Tools API** (FastAPI) as OpenAPI tools.

---

### 4.2 Architecture Diagram (Mermaid)

You can paste this into a Mermaid-enabled viewer (or draw.io / Excalidraw):

```mermaid
flowchart TD
    subgraph Data
        sales[Sales Data]
        support[Support Data]
        marketing[Marketing Data]
    end

    subgraph Tools
        slack[Slack Notifier]
        email[Email Sender]
        task[Task Manager]
        pdf[PDF Report Generator]
        openapi["Agent Tools API (FastAPI)"]
    end

    subgraph Memory
        mem[MemoryBank]
        kb[KnowledgeBase]
        sessions[SessionService]
    end

    subgraph Agents
        dc[DataCollectorAgent]
        an[AnalyticsAgent]
        rc[RootCauseAgent]
        dm[DecisionMakerAgent]
        llm[LLMReasoningAgent (Gemini)]
        act[ActionExecutorAgent]
        sup[SupervisorAgent]
    end

    sales --> dc
    support --> dc
    marketing --> dc

    dc --> an
    an --> rc
    rc --> dm
    dm --> llm
    llm --> act

    sup --> dc
    sup --> an
    sup --> rc
    sup --> dm
    sup --> llm
    sup --> act

    act --> slack
    act --> email
    act --> task
    act --> pdf
    act --> openapi

    sup --> mem
    sup --> kb
    sup --> sessions
    kb --> llm
```

## 5. 🧩 Key Features (mapped to course concepts)

This project explicitly demonstrates multiple agent concepts from the course:

### Multi-Agent System

Sequential agents: DataCollector → Analytics → RootCause → Decision → LLM → Action.

Specialized responsibilities per agent to keep logic clean.

### Tools (Custom + OpenAPI)

Custom tools: SlackNotifier, EmailSender, TaskManager, PDFReportGenerator, DataFetcher.

OpenAPI tools: OpenAPISlack, OpenAPITask using `agent_tools_api/main.py` (FastAPI).

### Sessions & Memory

SessionService manages long-running sessions, active/paused/finished, and last trace ID.

MemoryBank stores incidents, KPI baselines and allows querying past events.

KnowledgeBase supports RAG-style similarity search over incidents.

### Long-Running Operations

SupervisorWithSession allows stepwise execution, pause/resume and continuation across sessions.

### Observability

Centralized logging via `src/utils/logger.py`.

Each step logs trace IDs, status and outcomes, making debugging easier.

### LLM-Powered Agent

LLMReasoningAgent uses Gemini (Vertex AI) for plan refinement and explanation generation.

---

## 6. 🛠 Tech Stack

- **Language:** Python 3
- **Agents & Orchestration:** Custom classes under `src/agents`
- **LLM:** Google Gemini via Vertex AI Python SDK
- **API Tools:** FastAPI (`src/agent_tools_api`)
- **Data:** CSVs under `data/` simulating enterprise signals
- **Packaging / Env:** `.env`, `Config` class in `src/config.py`

---

## 7. 🚀 Getting Started (Local Demo)

### 7.1 Prerequisites

- Python 3.10+
- (Optional) Google Cloud project + Vertex AI enabled if you want real Gemini calls.

### 7.2 Setup

```bash
git clone https://github.com/nikhilvadlaa/AIOCC-Enterprise-Agent.git
cd AIOCC-Enterprise-Agent

# Create virtual env (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set values in `.env`:

For demo mode only, you can set:

```ini
DEMO_MODE=true
```

Leave Slack / email keys empty → actions are logged instead of sent.

For full integration (optional):

- `GCP_PROJECT_ID`, `GCP_LOCATION`
- `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`
- `SENDGRID_API_KEY` or SMTP settings

### 7.3 Run a Single Incident Cycle

```bash
python run_cycle.py
```

You should see logs like:

- Data loaded
- Insights computed
- Root cause identified
- Plan created and refined
- Actions (Slack/email/task/report) simulated or executed
- Incident stored in `memory.json`

---

## 8. ☁️ Deployment Overview

This project is container-ready and includes Cloud Run instructions.

- `Dockerfile` — builds the agent container.
- `src/agent_tools_api/Dockerfile` — builds the tools API container.
- `DEPLOYMENT_GUIDE.md` — detailed steps for:
  - Local Docker
  - Google Cloud Run Service / Jobs
  - Environment variables and secret handling

For the competition, I describe deployment in the write-up and show how this could run as:

- A scheduled Cloud Run job (periodic incident scan).
- A Cloud Run service with an HTTP endpoint to trigger a new cycle.

---

## 9. 📊 Example Use Cases

- **E-commerce platform** wanting automatic detection of “marketing spike → traffic spike → infrastructure stress”.
- **SaaS product** needing root cause suggestions for support ticket spikes.
- **Internal infrastructure teams** wanting a Gemini-powered incident analyst.

---
