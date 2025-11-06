# Manual Server Setup Script for CareConnect
# Run this once to prepare your Hetzner server

Write-Host "==================================="
Write-Host "CareConnect Server Setup"
Write-Host "==================================="
Write-Host ""

$serverHost = "46.62.253.61"
$serverUser = "root"

Write-Host "This script will set up your server at $serverHost"
Write-Host ""
Write-Host "Steps:"
Write-Host "1. Install Docker"
Write-Host "2. Create /app/careconnect directory"
Write-Host "3. Copy docker-compose.prod.yml to server"
Write-Host "4. Create .env file"
Write-Host ""

# Step 1: Install Docker
Write-Host "Step 1: Installing Docker on server..."
ssh ${serverUser}@${serverHost} @"
apt-get update && apt-get install -y curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
mkdir -p /app/careconnect
"@

# Step 2: Copy docker-compose file
Write-Host ""
Write-Host "Step 2: Copying docker-compose.prod.yml to server..."
scp docker-compose.prod.yml ${serverUser}@${serverHost}:/app/careconnect/

# Step 3: Check what was copied
Write-Host ""
Write-Host "Step 3: Verifying files on server..."
ssh ${serverUser}@${serverHost} "ls -la /app/careconnect/"

Write-Host ""
Write-Host "==================================="
Write-Host "Setup Complete!"
Write-Host "==================================="
Write-Host ""
Write-Host "Now you can deploy by pushing to the prod branch:"
Write-Host "  git push origin prod"
Write-Host ""
Write-Host "Or manually pull and start containers:"
Write-Host "  ssh root@46.62.253.61"
Write-Host "  cd /app/careconnect"
Write-Host "  docker compose -f docker-compose.prod.yml pull"
Write-Host "  docker compose -f docker-compose.prod.yml up -d"
Write-Host ""
