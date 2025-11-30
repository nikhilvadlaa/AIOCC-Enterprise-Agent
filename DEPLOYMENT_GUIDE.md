# Deployment Guide

This project is designed to be cloud-native and container-ready. While it can be run locally, it includes all necessary configurations for deployment to Google Cloud Platform.

## 🐳 Option 1: Docker (Local or Server)

The application is containerized using `Dockerfile`.

### Build the Image
```bash
docker build -t aiocc-agent .
```

### Run the Container
```bash
docker run --env-file .env aiocc-agent
```

## ☁️ Option 2: Google Cloud Run (Serverless)

You can deploy this agent as a serverless job or service on Google Cloud Run.

### Prerequisites
1.  Google Cloud Project with Billing enabled.
2.  `gcloud` CLI installed and authenticated.

### Deployment Steps

1.  **Submit Build to Container Registry**:
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/aiocc-agent
    ```

2.  **Deploy to Cloud Run**:
    ```bash
    gcloud run jobs deploy aiocc-job \
      --image gcr.io/YOUR_PROJECT_ID/aiocc-agent \
      --region us-central1
    ```

3.  **Execute the Job**:
    ```bash
    gcloud run jobs execute aiocc-job
    ```

## 🔐 Secret Management
For production deployment, do not use `.env` files. Instead, use **Google Secret Manager** to securely store:
-   `SLACK_BOT_TOKEN`
-   `SENDGRID_API_KEY`
-   `GCP_PROJECT_ID`

Refer to the `src/tools` implementation to see how secrets are injected at runtime.
