# 🚀 Deployment Guide — AIOCC Enterprise Agent

This guide explains how to run AIOCC in a **cloud-native** way using:

1. Local Docker
2. Google Cloud Run (Service or Job)
3. Agent Tools API (OpenAPI tools)

---

## 1. 🐳 Option 1: Local Docker

### 1.1 Build the image

```bash
docker build -t aiocc-agent .
```

### 1.2 Run the container

```bash
docker run \
  --env-file .env \
  -v $(pwd)/memory.json:/app/memory.json \
  aiocc-agent
```

This will:

- Load data from `data/`
- Run one full incident cycle
- Store incident history in `memory.json`

---

## 2. ☁️ Option 2: Google Cloud Run (Service)

### 2.1 Prerequisites

- Google Cloud project
- `gcloud` CLI installed and authenticated
- Vertex AI and Cloud Run enabled

```bash
gcloud services enable run.googleapis.com aiplatform.googleapis.com
```

### 2.2 Build & push image

```bash
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/aiocc-agent
```

### 2.3 Deploy as a Cloud Run service

Assume you wrap `run_cycle` into a FastAPI endpoint (e.g. `main.py` `/run_cycle`):

```bash
gcloud run deploy aiocc-agent-service \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/aiocc-agent \
  --platform managed \
  --region $GCP_LOCATION \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$GOOGLE_CLOUD_PROJECT,GCP_LOCATION=$GCP_LOCATION,DEMO_MODE=true
```

You will get a URL like:

`https://aiocc-agent-service-xxxxxx-uc.a.run.app`

This can be called by CI/CD, a dashboard button, or another agent.

---

## 3. ⏱ Option 3: Cloud Run Jobs (Scheduled)

If you want AIOCC to run periodically (e.g. every 5 minutes):

### 3.1 Create the job

```bash
gcloud run jobs create aiocc-job \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/aiocc-agent \
  --region $GCP_LOCATION \
  --set-env-vars GCP_PROJECT_ID=$GOOGLE_CLOUD_PROJECT,GCP_LOCATION=$GCP_LOCATION,DEMO_MODE=true
```

### 3.2 Execute manually

```bash
gcloud run jobs execute aiocc-job --region $GCP_LOCATION
```

### 3.3 Schedule with Cloud Scheduler (optional)

Use Cloud Scheduler to hit the job at your desired interval.

---

## 4. 🧰 Agent Tools API (OpenAPI)

The project includes a FastAPI tools service in `src/agent_tools_api/main.py` which exposes:

- `/openapi/slack` — send Slack messages
- `/openapi/task` — create external tasks/tickets
- `/email` — send emails via SendGrid/SMTP

### 4.1 Local run

```bash
cd src/agent_tools_api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 4.2 Docker build

```bash
docker build -t aiocc-tools -f src/agent_tools_api/Dockerfile .
docker run -p 8080:8080 --env-file .env aiocc-tools
```

The main agent uses this via `src/tools/openapi_tools.py`.

---

## 5. 🔐 Secrets & Environment

For a real deployment, prefer secret managers instead of `.env`:

- `GCP_PROJECT_ID`, `GCP_LOCATION`
- `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`
- `SENDGRID_API_KEY` or SMTP credentials

Cloud Run supports environment variables from Secret Manager — recommended for production.

---

## 6. 🧪 Demo vs Production Modes

- **`DEMO_MODE=true`**
  - Skips external API calls (or logs instead).
  - Safe for local testing / competition demo.

- **`DEMO_MODE=false`**
  - Uses real Gemini + Slack + Email + Tools API (if configured).
