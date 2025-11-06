# CareConnect Deployment Guide

This guide will help you deploy CareConnect to your Hetzner server using GitHub Actions and Docker.

## Server Information

- **IPv4**: 46.62.253.61
- **IPv6**: 2a01:4f9:c013:892c::/64
- **User**: root
- **Deployment Directory**: /app/careconnect

## Prerequisites

1. GitHub account with admin access to the repository
2. Hetzner server (already provisioned)
3. GitHub Personal Access Token (PAT) with `packages:read` and `packages:write` permissions
4. OpenAI API key
5. SendGrid API key (optional, for email notifications)

## Step 1: Set Up Your Server

### Option A: Automated Setup (Recommended)

1. SSH into your server:
```bash
ssh root@46.62.253.61
```

2. Download and run the setup script:
```bash
curl -o setup-server.sh https://raw.githubusercontent.com/Hadi-Hsn/CareConnect/main/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

### Option B: Manual Setup

1. SSH into your server:
```bash
ssh root@46.62.253.61
```

2. Install Docker and Docker Compose:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

3. Create application directory:
```bash
mkdir -p /app/careconnect
cd /app/careconnect
```

4. Configure firewall:
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5173/tcp
ufw allow 8000/tcp
ufw enable
```

## Step 2: Configure Environment Variables

1. On your server, create the `.env` file:
```bash
cd /app/careconnect
nano .env
```

2. Add your environment variables (use `.env.production.example` as a template):
```bash
# Database Configuration
POSTGRES_USER=careconnect
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=careconnect

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=3072

# JWT Configuration
JWT_SECRET=your_very_secure_jwt_secret_change_this
JWT_EXPIRATION_MINUTES=1440

# Frontend Configuration
FRONTEND_ORIGIN=http://46.62.253.61:5173
VITE_API_BASE_URL=http://46.62.253.61:8000/api/v1

# Email Configuration
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=CareConnect
ADMIN_EMAILS=admin@yourdomain.com

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
```

3. Copy the production docker-compose file:
```bash
cd /app/careconnect
wget https://raw.githubusercontent.com/Hadi-Hsn/CareConnect/main/docker-compose.prod.yml
```

## Step 3: Set Up GitHub Secrets

1. Go to your GitHub repository: https://github.com/Hadi-Hsn/CareConnect
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GHCR_PAT` | `ghp_xxxxxxxxxxxx` | GitHub Personal Access Token with `packages:read` and `packages:write` |
| `SERVER_HOST` | `46.62.253.61` | Your Hetzner server IP |
| `SERVER_USER` | `root` | SSH username |
| `SERVER_PASS` | `P@ss@123` | SSH password (consider using SSH keys instead) |

### Creating a GitHub Personal Access Token (PAT)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "CareConnect GHCR"
4. Select the following scopes:
   - `write:packages`
   - `read:packages`
   - `delete:packages` (optional)
5. Click "Generate token"
6. Copy the token and save it as the `GHCR_PAT` secret

## Step 4: Deploy

### Automatic Deployment (via GitHub Actions)

Simply push to the `main` branch:

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Build Docker images for backend and frontend
2. Push images to GitHub Container Registry
3. SSH into your server
4. Pull the latest images
5. Restart the containers

### Manual Deployment

If you need to deploy manually:

```bash
# SSH into server
ssh root@46.62.253.61

# Navigate to app directory
cd /app/careconnect

# Login to GitHub Container Registry
echo YOUR_GHCR_PAT | docker login ghcr.io -u Hadi-Hsn --password-stdin

# Pull latest images
docker pull ghcr.io/hadi-hsn/careconnect-backend:latest
docker pull ghcr.io/hadi-hsn/careconnect-frontend:latest

# Deploy
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

## Step 5: Verify Deployment

1. Check if containers are running:
```bash
docker compose -f docker-compose.prod.yml ps
```

2. View logs:
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f db
```

3. Access the application:
   - Frontend: http://46.62.253.61:5173
   - Backend API: http://46.62.253.61:8000
   - API Docs: http://46.62.253.61:8000/docs

## Monitoring and Maintenance

### View Logs

```bash
# Real-time logs
docker compose -f docker-compose.prod.yml logs -f

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
```

### Restart Services

```bash
# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend
```

### Update Application

```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Recreate containers
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Database Backup

```bash
# Create backup
docker exec careconnect-db pg_dump -U careconnect careconnect > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
cat backup_20250107_120000.sql | docker exec -i careconnect-db psql -U careconnect careconnect
```

### Clean Up Old Images

```bash
docker image prune -f
```

## Troubleshooting

### Containers won't start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check if ports are available
netstat -tulpn | grep -E ':(80|443|5173|8000|5432)'
```

### Database connection issues

```bash
# Check if database is healthy
docker exec careconnect-db pg_isready -U careconnect

# Connect to database
docker exec -it careconnect-db psql -U careconnect
```

### Cannot pull images

```bash
# Re-login to GHCR
echo YOUR_GHCR_PAT | docker login ghcr.io -u Hadi-Hsn --password-stdin

# Make sure images are public or you have access
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes -f
```

## Security Recommendations

1. **Change default password**: Update the server root password
2. **Use SSH keys**: Replace password authentication with SSH keys
3. **Set up SSL/TLS**: Use Let's Encrypt with nginx reverse proxy
4. **Enable firewall**: Restrict access to only necessary ports
5. **Regular updates**: Keep Docker and system packages updated
6. **Backup regularly**: Set up automated database backups
7. **Monitor logs**: Set up log aggregation and monitoring
8. **Use secrets management**: Consider using Docker secrets or a secrets manager

## Domain Setup (Optional)

To use a custom domain instead of IP:

1. Point your domain's A record to `46.62.253.61`
2. Update `.env` file:
```bash
FRONTEND_ORIGIN=https://yourdomain.com
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```
3. Set up nginx reverse proxy with SSL (Let's Encrypt)

## Support

For issues or questions:
- Check logs: `docker compose -f docker-compose.prod.yml logs`
- Review GitHub Actions runs: https://github.com/Hadi-Hsn/CareConnect/actions
- Check container status: `docker compose -f docker-compose.prod.yml ps`

## Useful Commands Reference

```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# Restart services
docker compose -f docker-compose.prod.yml restart

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check status
docker compose -f docker-compose.prod.yml ps

# Execute command in container
docker exec -it careconnect-backend bash

# Update and restart
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --force-recreate
```
