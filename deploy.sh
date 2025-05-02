#!/bin/bash

# Set variables
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="weather-mcp-server"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build the Docker image
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID