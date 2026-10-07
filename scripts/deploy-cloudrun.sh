#!/usr/bin/env bash
# Deploy the FastAPI backend to Cloud Run (Singapore) from local source.
# Cloud Build builds the image in the cloud; no local Docker is needed.
#
# Prerequisites:
#   gcloud auth login
#   gcloud config set project <PROJECT_ID>
#   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
#
# Migrations are NOT run by this script and NOT at container start. Apply them
# separately, with the DIRECT (non-pooled) Neon URL, from a machine that can
# reach Neon (the Cloud Run container is not used for this):
#   cd backend
#   MIGRATION_DATABASE_URL='postgresql://...@ep-xxxx.ap-southeast-1.aws.neon.tech/thesis?sslmode=require' \
#     uv run python -m scripts.migrate
#
# Real secrets (DATABASE_URL now, LLM_API_KEY later) live in Google Secret
# Manager, not in a file and not in this script; see the example at the bottom.

set -euo pipefail

SERVICE="${SERVICE:-thesis-multi-agent-api}"
REGION=asia-southeast1
# Exact origin of the deployed frontend. Keep in sync with ALLOWED_ORIGINS in
# backend/.env.example. JSON list; add more origins with a comma inside the
# brackets and switch --set-env-vars to a custom delimiter (^@^KEY=v@KEY=v).
FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-https://<deployed-frontend-origin>}"

# --timeout 3600 is the Cloud Run service maximum (default 300 s): the LangGraph
# evaluation batch runs inside one long request.
# https://cloud.google.com/run/docs/configuring/request-timeout (verified 2026-10-07)
#
# --max-instances bounds pressure on Neon. Every container opens its own psycopg
# pool, and the pooled endpoint multiplexes up to 10,000 client connections into
# a per-user pool of 90% of the compute's max_connections. Raise this only with
# a Neon compute size that matches, and keep the in-container pool small.
# https://neon.com/docs/connect/connection-pooling (verified 2026-10-07)
gcloud run deploy "$SERVICE" \
  --source ./backend \
  --region "$REGION" \
  --allow-unauthenticated \
  --timeout 3600 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "ENV=production,COOKIE_SECURE=true,ALLOWED_ORIGINS=[\"$FRONTEND_ORIGIN\"]"

# Add the database URL from Secret Manager by appending this flag, or by running
# `gcloud run services update "$SERVICE" --region "$REGION"` with it:
#   --set-secrets "DATABASE_URL=neon-database-url:latest"
