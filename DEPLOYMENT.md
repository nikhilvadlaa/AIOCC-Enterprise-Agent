# Enterprise AIOps Deployment Guide

This guide details how to deploy the AIOps system to Google Cloud Platform (GCP) using Cloud Run and Cloud Build.

## Prerequisites

1.  **GCP Project**: A Google Cloud Project with billing enabled.
2.  **APIs Enabled**:
    -   Cloud Run API
    -   Cloud Build API
    -   Secret Manager API
    -   Vertex AI API
3.  **Service Account**: A service account with permissions to deploy to Cloud Run and access Secret Manager.

## Step 1: Secret Management

Store your API keys in Google Secret Manager:

```bash
# Slack
echo -n "your-slack-bot-token" | gcloud secrets create SLACK_BOT_TOKEN --data-file=-
# SendGrid
echo -n "your-sendgrid-api-key" | gcloud secrets create SENDGRID_API_KEY --data-file=-
# Trello
echo -n "your-trello-api-key" | gcloud secrets create TRELLO_API_KEY --data-file=-
echo -n "your-trello-token" | gcloud secrets create TRELLO_TOKEN --data-file=-
```

## Step 2: Manual Deployment

You can trigger a build and deploy manually from your local machine:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

This command will:
1.  Build the Docker image.
2.  Push it to Google Container Registry (GCR).
3.  Deploy the image to Cloud Run with the environment variables linked to the secrets.

## Step 3: CI/CD with GitHub Actions

1.  **Configure Workload Identity Federation**:
    -   Create a Workload Identity Pool and Provider.
    -   Grant the GitHub Actions Service Account access to the Provider.
    -   Bind the Service Account to the Workload Identity Pool.

2.  **Add Secrets to GitHub**:
    -   `GCP_PROJECT_ID`: Your GCP project ID.
    -   `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full resource name of the Workload Identity Provider (e.g., `projects/123456789/locations/global/workloadIdentityPools/my-pool/providers/my-provider`).
    -   `GCP_SERVICE_ACCOUNT`: The email of the Service Account used for deployment (e.g., `deployer@my-project.iam.gserviceaccount.com`).

3.  **Trigger Deployment**:
    -   Push to the `main` branch to trigger the workflow.

## Verification

1.  Go to the Cloud Run console.
2.  Check the logs for the `aiocc-runner` service.
3.  You should see logs indicating the agents are running and the cycle is executing.
