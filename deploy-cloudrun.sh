#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying Skylos AI to Google Cloud Run"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not installed"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and configure your GEMINI_API_KEY"
    exit 1
fi

# Get GEMINI_API_KEY from .env
GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d '=' -f2)
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not configured in .env"
    exit 1
fi

# Set project variables
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
SERVICE_NAME=${SERVICE_NAME:-skylos-ai-demo}
REGION=${REGION:-us-central1}

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Service Name: $SERVICE_NAME"
echo "   Region: $REGION"

# Build frontend
echo "📦 Building frontend..."
(cd frontend && npm install && npm run build)

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY"

echo "✅ Deployment complete!"
echo "🌐 Your app is available at:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'