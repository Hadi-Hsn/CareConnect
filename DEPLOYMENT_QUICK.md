# CareConnect Deployment - Quick Start

## 🚀 Quick Deployment Steps

### 1. Server Setup (One-time)

```bash
# SSH into your server
ssh root@46.62.253.61

# Run setup script (installs Docker, creates directories)
curl -fsSL https://raw.githubusercontent.com/Hadi-Hsn/CareConnect/main/setup-server.sh | bash

# Create application directory
mkdir -p /app/careconnect
cd /app/careconnect

# Copy production compose file
wget https://raw.githubusercontent.com/Hadi-Hsn/CareConnect/main/docker-compose.prod.yml

# Note: .env file will be auto-generated from GitHub Secrets during deployment
```

### 2. GitHub Secrets Setup (One-time)

Go to: https://github.com/Hadi-Hsn/CareConnect/settings/secrets/actions

Add these secrets (see GITHUB_SECRETS.md for details):

**Required:**
- `SERVER_HOST` - `46.62.253.61`
- `SERVER_USER` - `root`
- `SERVER_PASS` - `P@ss@123`
- `OPENAI_API_KEY` - Your OpenAI API key (from https://platform.openai.com/api-keys)

**Optional (for email features):**
- `SENDGRID_API_KEY` - Your SendGrid API key
- `EMAIL_FROM` - Your sender email (e.g., noreply@yourdomain.com)
- `ADMIN_EMAILS` - Comma-separated admin emails

**Note:** JWT_SECRET and POSTGRES_PASSWORD are hardcoded in the workflow (no secrets needed)

### 3. Deploy

```bash
# Push to trigger automatic deployment
git push origin main
```

Or manually:
```bash
ssh root@46.62.253.61
cd /app/careconnect
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 🔗 Access Points

- **Frontend**: http://46.62.253.61:5173
- **Backend API**: http://46.62.253.61:8000
- **API Docs**: http://46.62.253.61:8000/docs

## 📊 Monitoring Commands

```bash
# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart
docker compose -f docker-compose.prod.yml restart
```

## 🔧 Common Tasks

### Update Application
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Backup Database
```bash
docker exec careconnect-db pg_dump -U careconnect careconnect > backup_$(date +%Y%m%d).sql
```

### View Backend Logs
```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

### Clean Up
```bash
docker system prune -f
docker image prune -a -f
```

## ⚠️ Important Notes

1. **First Deployment**: Initial setup may take 5-10 minutes
2. **Environment Variables**: Always set in `/app/careconnect/.env`
3. **Security**: Change default passwords immediately
4. **Backups**: Set up regular database backups
5. **Monitoring**: Check logs regularly for errors

## 📝 Required Environment Variables

All secrets are managed through GitHub Secrets (no manual .env file needed):

**Critical:**
```env
OPENAI_API_KEY=sk-...           # Required - Get from OpenAI
```

**Optional (Email features):**
```env
SENDGRID_API_KEY=SG....         # For sending emails
EMAIL_FROM=noreply@domain.com   # Sender email
ADMIN_EMAILS=admin@domain.com   # Handover notifications
```

**Hardcoded (no secret needed):**
```env
JWT_SECRET=8f7d6c5b4a3e2d1c...  # Hardcoded in workflow
POSTGRES_PASSWORD=careconnect_prod_2025  # Hardcoded in workflow
```

See [GITHUB_SECRETS.md](./GITHUB_SECRETS.md) for complete guide.

## 🆘 Troubleshooting

**Containers won't start?**
```bash
docker compose -f docker-compose.prod.yml logs
```

**Database issues?**
```bash
docker exec careconnect-db pg_isready -U careconnect
```

**Out of space?**
```bash
docker system prune -a --volumes -f
```

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete guide.
