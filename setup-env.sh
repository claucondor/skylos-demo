#!/bin/bash

# Script to setup environment variables on the VM
# Usage: ./setup-env.sh <INSTANCE_NAME> <ZONE> <GEMINI_API_KEY>

INSTANCE_NAME=${1:-skylos-ai-vm}
ZONE=${2:-us-central1-a}
GEMINI_API_KEY=$3

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY is required"
    echo "Usage: ./setup-env.sh <INSTANCE_NAME> <ZONE> <GEMINI_API_KEY>"
    exit 1
fi

echo "🔑 Setting up environment variables on VM..."

gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    cd ~/skylos-ai
    echo 'GEMINI_API_KEY=$GEMINI_API_KEY' > .env
    
    # Restart the service to pick up new environment
    sudo systemctl restart skylos-ai
    
    echo '✅ Environment configured and service restarted'
"

echo "✅ Environment setup complete!"