#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying Skylos AI to Google Cloud VM"
echo "========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not installed"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project variables
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
INSTANCE_NAME=${INSTANCE_NAME:-skylos-ai-vm}
ZONE=${ZONE:-us-central1-a}
MACHINE_TYPE=${MACHINE_TYPE:-e2-medium}

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Instance Name: $INSTANCE_NAME"
echo "   Zone: $ZONE"
echo "   Machine Type: $MACHINE_TYPE"

# Create VM instance
echo "🖥️  Creating VM instance..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --tags=http-server,https-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring

# Create firewall rule for the application
echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create allow-skylos-ai \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow access to Skylos AI on port 8000" \
    --target-tags http-server || echo "Firewall rule might already exist"

echo "⏳ Waiting for VM to be ready..."
sleep 30

echo "📁 Copying files to VM..."
gcloud compute scp --recurse . $INSTANCE_NAME:~/skylos-ai --zone=$ZONE

echo "🔧 Setting up VM..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    # Update system
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv nodejs npm git curl

    # Install uv (Python package manager)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.cargo/env

    # Setup application
    cd ~/skylos-ai
    
    # Install Python dependencies
    ~/.cargo/bin/uv sync
    
    # Build frontend
    cd frontend
    npm install
    npm run build
    cd ..
"

# Create systemd service file
echo "📝 Creating systemd service..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    sudo tee /etc/systemd/system/skylos-ai.service > /dev/null <<'EOF'
[Unit]
Description=Skylos AI Demo
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/skylos-ai
Environment=PATH=/home/$USER/.cargo/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/$USER/.cargo/bin/uv run python api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable skylos-ai
    sudo systemctl start skylos-ai
"

# Get VM external IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: http://$EXTERNAL_IP:8000"
echo "📊 Check service status: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo systemctl status skylos-ai'"
echo "📝 View logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo journalctl -u skylos-ai -f'"