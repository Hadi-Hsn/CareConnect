#!/bin/bash

# CareConnect Server Setup Script for Hetzner
# This script prepares the server for Docker deployment

set -e

echo "==================================="
echo "CareConnect Server Setup"
echo "==================================="

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully"
else
    echo "Docker is already installed"
fi

# Install Docker Compose
echo "Installing Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose is already installed"
fi

# Create application directory
echo "Creating application directory..."
mkdir -p /app/careconnect
cd /app/careconnect

# Create .env file template
echo "Creating .env file template..."
cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=careconnect
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
POSTGRES_DB=careconnect

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=3072

# JWT Configuration
JWT_SECRET=CHANGE_THIS_TO_RANDOM_SECRET
JWT_EXPIRATION_MINUTES=1440

# Frontend Configuration
FRONTEND_ORIGIN=http://46.62.253.61:5173
VITE_API_BASE_URL=http://46.62.253.61:8000/api/v1

# Email Configuration (SendGrid)
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=CareConnect
ADMIN_EMAILS=admin@yourdomain.com

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

echo "Created .env template at /app/careconnect/.env"

# Configure firewall (UFW)
echo "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 5173/tcp
    ufw allow 8000/tcp
    ufw --force enable
    echo "Firewall configured"
fi

# Set up log rotation
echo "Setting up log rotation..."
cat > /etc/logrotate.d/careconnect << 'EOF'
/app/careconnect/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
EOF

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit /app/careconnect/.env with your actual credentials"
echo "2. Copy docker-compose.prod.yml to /app/careconnect/"
echo "3. Set up GitHub secrets in your repository:"
echo "   - GHCR_PAT: GitHub Personal Access Token with packages:read/write"
echo "   - SERVER_HOST: 46.62.253.61"
echo "   - SERVER_USER: root"
echo "   - SERVER_PASS: Your server password"
echo "4. Push to main branch to trigger deployment"
echo ""
echo "Manual deployment command:"
echo "cd /app/careconnect && docker compose -f docker-compose.prod.yml up -d"
echo ""
