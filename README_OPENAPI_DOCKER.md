# AIOCC — OpenAPI Tools & Docker Deployment

## Summary
This repository includes:
- `agent_tools_api/` — FastAPI server exposing OpenAPI endpoints for Slack, Email, Task (Trello).
- `openapi_specs/` — OpenAPI YAML specs for tools.
- `src/tools/openapi_tools.py` — OpenAPI client wrapper used by agents.
- Docker compose to run both tools API and your AIOCC runner.

## Setup (local)
1. Copy `.env.example` to `.env` and set any real API keys you have (optional).
2. Build & run with Docker Compose:
   ```bash
   docker compose up --build
