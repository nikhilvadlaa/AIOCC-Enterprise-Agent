# Competition Submission Details

## 3️⃣ Competition Write-Up (Kaggle submission text)

### Track
Enterprise Agents

### Title
AIOCC — Enterprise AIOps Control Center

### Problem

Modern SRE and operations teams are overwhelmed by alerts, dashboards and manual runbooks. In a typical incident, engineers jump between monitoring tools, ticketing systems and chat, trying to correlate signals and figure out: *What happened? Why? What do we do now?*

This leads to:

- High Mean Time To Resolution (MTTR)
- Alert fatigue and burnout
- Repeated manual work for common incident patterns

Most of these incidents are not “new problems” — they follow repeatable patterns that could be handled by agents.

### Solution

AIOCC (AI Operations Control Center) is a multi-agent AIOps system that simulates an enterprise environment and automates the full loop:

1. Ingests synthetic “signals” (sales, support, marketing) that mimic load and customer demand.
2. Detects anomalies and aggregates them into incidents.
3. Identifies likely root causes by correlating anomalies.
4. Proposes and refines remediation plans using Gemini.
5. Executes actions via tools (Slack, email, tickets, PDF reports).
6. Stores incidents in a memory bank and knowledge base for reuse (RAG).

Instead of just alerting, AIOCC behaves like a self-healing co-pilot, helping teams understand incidents faster and apply high-quality, consistent remediation.

### Why Agents?

The workflow is naturally agentic:

- A **DataCollectorAgent** focuses on loading and preparing data.
- An **AnalyticsAgent** specializes in computing KPIs and finding anomalies.
- A **RootCauseAgent** reasons over anomalies across datasets.
- A **DecisionMakerAgent** transforms root causes into an initial remediation plan.
- An **LLMReasoningAgent (Gemini)** refines the plan and provides explanations using a knowledge base.
- An **ActionExecutorAgent** focuses on integrating with external tools (Slack, email, ticket/task system, PDF generator).
- A **SupervisorAgent** orchestrates the whole flow, while **SupervisorWithSession** adds long-running session semantics.

This division of labor makes the system easier to extend and aligns well with the agent patterns from the course.

### Architecture

The system has four main layers:

1. **Data & Signals**
   - CSV files for sales, support and marketing simulate real observability signals.
   - A `DataFetcher` tool loads and validates the data.

2. **Agents**
   - `DataCollectorAgent` → `AnalyticsAgent` → `RootCauseAgent` → `DecisionMakerAgent` → `LLMReasoningAgent` → `ActionExecutorAgent`
   - `SupervisorAgent` coordinates one full incident cycle, logs steps and writes to memory.
   - `SupervisorWithSession` adds session management (active / paused / finished, last trace ID).

3. **Tools & Integrations**
   - Custom tools: `SlackNotifier`, `EmailSender`, `PDFReportGenerator`, `TaskManager`.
   - OpenAPI tools: `OpenAPISlack`, `OpenAPITask` hitting a FastAPI service (`agent_tools_api/main.py`) that exposes HTTP endpoints for Slack and tasks.

4. **Memory & Knowledge**
   - `MemoryBank` stores incidents, KPI baselines and allows querying by type.
   - `KnowledgeBase` provides RAG-style retrieval over historic incidents.
   - `SessionService` manages sessions as JSON, supporting pause and resume.

A Gemini-powered `LLMReasoningAgent` runs on top of Vertex AI. It refines remediation plans and generates human-readable explanations using the current insights, root cause analysis and similar past incidents.

### Features (mapped to course concepts)

This project implements multiple course concepts:

1. **Multi-Agent System**
   - Several specialized agents working together in a sequential workflow.
2. **Tools (Custom + OpenAPI)**
   - Custom tools for Slack, email, tasks, PDF, and data loading.
   - OpenAPI tools via an Agent Tools API (FastAPI) consumed from the main agent.
3. **Sessions & Memory**
   - File-backed sessions with state and last trace ID.
   - Memory bank for incidents and KPI baselines.
   - A simple knowledge base for RAG on past incidents.
4. **Long-Running Operations**
   - SupervisorWithSession supports pause/resume semantics for longer workflows.
5. **Observability**
   - Centralized logging with trace IDs and step markers.
6. **LLM Agent (Gemini)**
   - LLMReasoningAgent calls Gemini for plan refinement and narrative explanations.

### Technical Implementation

The project is written in Python and organized under `src/`:

- `src/agents` – all agent classes.
- `src/tools` – integration tools and utilities.
- `src/services` – memory, sessions, knowledge base, logging.
- `src/config.py` – configuration and environment handling.
- `src/agent_tools_api` – FastAPI service exposing tools via HTTP/OpenAPI.
- `run_cycle.py` – entry point to run a single incident cycle end-to-end.

For deployment, the project is containerized via `Dockerfile` and can run locally or on Google Cloud Run. An additional Dockerfile exists for the Agent Tools API.

### Impact and Future Work

Even though the data is synthetic, the overall design mirrors how an enterprise could implement a self-healing AIOps co-pilot. In a real system, data sources would be:

- Monitoring systems (metrics, logs, traces)
- Ticketing systems
- Release pipelines and change events

Future work could include:

- Stronger anomaly detection models.
- Deeper integration with real observability platforms.
- A UI for exploring incidents, past resolutions and runbook suggestions.

This project demonstrates how agents, tools, memory and LLM reasoning can come together to reduce MTTR and improve reliability in an enterprise environment.

---

## 4️⃣ 3-Minute Video Script (YouTube)

**[0:00 – 0:10] — Intro**
*Visual: Slide “AIOCC — Enterprise AIOps Control Center” + your face cam (optional)*
**Audio:**
"Hi, I’m [Your Name], and this is AIOCC — an enterprise AIOps control center that turns noisy alerts into autonomous, self-healing actions."

**[0:10 – 0:30] — The Problem**
*Visual: Slide with icons: alerts, dashboards, tired engineer.*
**Audio:**
"In most companies, SRE and ops teams are drowning in alerts, dashboards and manual runbooks. Every incident feels like detective work: jump between monitoring, tickets and chat, try to connect the dots and then run manual fixes. This means high MTTR, alert fatigue and a lot of repetitive work."

**[0:30 – 0:50] — The Idea**
*Visual: Slide “From Alerts → Autonomous Remediation”*
**Audio:**
"My idea was to build an agentic AIOps co-pilot that doesn’t just alert you, but actually investigates, finds the root cause and executes remediation steps — and then remembers what happened for next time."

**[0:50 – 1:20] — Architecture & Agents**
*Visual: Architecture diagram (Mermaid exported or hand-drawn).*
**Audio:**
"AIOCC is built as a multi-agent system. A DataCollectorAgent loads synthetic sales, support and marketing data that simulate real signals. An AnalyticsAgent computes KPIs and flags anomalies. A RootCauseAgent correlates those anomalies and proposes likely root causes. Then a DecisionMakerAgent creates a remediation plan, and an LLMReasoningAgent powered by Gemini refines that plan and explains what’s going on. Finally, an ActionExecutorAgent sends Slack messages, emails, creates tasks and generates a PDF incident report. All of this is orchestrated by a SupervisorAgent, with a SupervisorWithSession wrapper that adds session state and long-running behavior."

**[1:20 – 1:50] — Tools, Memory & Gemini**
*Visual: Show code or terminal logs; highlight Gemini and memory.*
**Audio:**
"The agents use several tools: custom Slack and email notifiers, a task manager, a PDF generator, and an Agent Tools API exposed via FastAPI and consumed as OpenAPI tools. A MemoryBank stores incidents and KPI baselines, while a KnowledgeBase lets the LLM do a simple RAG over past incidents. The LLMReasoningAgent calls Gemini on Vertex AI to refine the remediation plan and generate human-readable explanations that reference similar incidents from the knowledge base."

**[1:50 – 2:20] — Demo**
*Visual: Run `python run_cycle.py`, scroll through logs; highlight key lines.*
**Audio:**
"Here’s a demo of a full incident cycle. The system loads data, detects an anomaly, finds a potential root cause and then builds a remediation plan. Gemini refines that plan and we can see the final actions: for example, notify a Slack channel, create a follow-up task and generate a PDF incident summary. The incident is also stored in memory for future runs."

**[2:20 – 2:45] — Deployment**
*Visual: Terminal with Docker build / Cloud Run commands; slide “Cloud-Native”.*
**Audio:**
"The project is container-ready with Docker, and I’ve included a deployment guide for Google Cloud Run. It can run as a Cloud Run service triggered by HTTP or as a scheduled Cloud Run job. The Agent Tools API also runs as its own FastAPI service."

**[2:45 – 3:00] — Closing**
*Visual: Slide “Why This Matters”.*
**Audio:**
"AIOCC shows how agents, tools, memory and Gemini can work together to reduce MTTR and make incident response smarter and less stressful. Thank you for watching, and I hope you enjoy exploring the code."
