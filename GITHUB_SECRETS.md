# GitHub Secrets Configuration

## 🔐 Required Secrets for CI/CD Pipeline

Add these secrets to your GitHub repository at:
**https://github.com/Hadi-Hsn/CareConnect/settings/secrets/actions**

Click **"New repository secret"** for each one.

---

## Server Access Secrets

### `SERVER_HOST`
- **Value**: `46.62.253.61`
- **Description**: Your Hetzner server IP address
- **Example**: `46.62.253.61`

### `SERVER_USER`
- **Value**: `root`
- **Description**: SSH username for your server
- **Example**: `root`

### `SERVER_PASS`
- **Value**: `P@ss@123`
- **Description**: SSH password for your server
- **Security Note**: ⚠️ Change this password after first login!
- **Better Alternative**: Use SSH keys instead of password authentication

---

## Application Configuration Secrets

### `OPENAI_API_KEY`
- **Value**: `sk-proj-xxxxxxxxxxxxxxxxxx`
- **Description**: OpenAI API key for GPT-4 and embeddings
- **Where to get it**: https://platform.openai.com/api-keys
- **Example**: `sk-proj-abcd1234efgh5678ijkl9012mnop3456`
- **Required**: ✅ Yes - Application won't work without it

### `SENDGRID_API_KEY`
- **Value**: `SG.xxxxxxxxxxxxxxxx`
- **Description**: SendGrid API key for sending emails
- **Where to get it**: https://app.sendgrid.com/settings/api_keys
- **Example**: `SG.abcd1234efgh5678.ijkl9012mnop3456qrst7890`
- **Required**: ⚠️ Optional - Emails won't work without it

### `EMAIL_FROM`
- **Value**: `noreply@yourdomain.com`
- **Description**: Sender email address for notifications
- **Example**: `noreply@careconnect.com`
- **Required**: ⚠️ Optional - Only needed if using SendGrid

### `ADMIN_EMAILS`
- **Value**: `admin@yourdomain.com,support@yourdomain.com`
- **Description**: Comma-separated list of admin emails for handover notifications
- **Example**: `admin@careconnect.com,support@careconnect.com`
- **Required**: ⚠️ Optional - Only needed for handover feature

---

## 🔧 Hardcoded Configuration (Not Secrets)

These values are hardcoded in the deployment workflow for simplicity:

### `JWT_SECRET`
- **Hardcoded Value**: `8f7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5`
- **Description**: Secret key for signing JWT tokens (authentication)
- **Note**: ⚠️ If you need to change this, edit `.github/workflows/deploy.yml` line with JWT_SECRET
- **Security**: Change this value if deploying to a public/production environment

### `POSTGRES_PASSWORD`
- **Hardcoded Value**: `careconnect_prod_2025`
- **Description**: PostgreSQL database password
- **Note**: ⚠️ If you need to change this, edit `.github/workflows/deploy.yml` line with POSTGRES_PASSWORD
- **Security**: Change this value if deploying to a public/production environment

---

## 📋 Complete Secrets Checklist

Copy this checklist when setting up:

**Required Secrets:**
- [ ] `SERVER_HOST` = `46.62.253.61`
- [ ] `SERVER_USER` = `root`
- [ ] `SERVER_PASS` = `P@ss@123`
- [ ] `OPENAI_API_KEY` = `sk-proj-...`

**Optional Secrets (for email features):**
- [ ] `SENDGRID_API_KEY` = `SG...`
- [ ] `EMAIL_FROM` = `noreply@yourdomain.com`
- [ ] `ADMIN_EMAILS` = `admin@yourdomain.com`

**Hardcoded (no secret needed):**
- [x] `JWT_SECRET` = Hardcoded in workflow
- [x] `POSTGRES_PASSWORD` = Hardcoded in workflow

---

## 🔑 How to Generate Secure Secrets

### JWT_SECRET
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})

# Or use online generator:
# https://generate-secret.vercel.app/64
```

### POSTGRES_PASSWORD
```bash
# On Linux/Mac:
openssl rand -base64 24

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) + (33,35,36,37,38,42,43,45,61) | Get-Random -Count 24 | % {[char]$_})

# Or manually create a strong password with:
# - At least 16 characters
# - Mix of uppercase, lowercase, numbers, symbols
```

---

## 🎯 Quick Setup Commands

### Add Secrets via GitHub CLI (Optional)

If you have GitHub CLI installed:

```bash
# Server access
gh secret set SERVER_HOST -b "46.62.253.61"
gh secret set SERVER_USER -b "root"
gh secret set SERVER_PASS -b "P@ss@123"

# Application secrets
gh secret set OPENAI_API_KEY -b "sk-proj-your-key-here"

# Optional: Email configuration
gh secret set SENDGRID_API_KEY -b "SG.your-key-here"
gh secret set EMAIL_FROM -b "noreply@yourdomain.com"
gh secret set ADMIN_EMAILS -b "admin@yourdomain.com"

# Note: JWT_SECRET and POSTGRES_PASSWORD are hardcoded in the workflow
```

---

## 🔍 Verify Secrets

After adding all secrets, go to:
https://github.com/Hadi-Hsn/CareConnect/settings/secrets/actions

You should see:

```
✓ ADMIN_EMAILS         Updated X minutes ago
✓ EMAIL_FROM           Updated X minutes ago
✓ OPENAI_API_KEY       Updated X minutes ago
✓ SENDGRID_API_KEY     Updated X minutes ago
✓ SERVER_HOST          Updated X minutes ago
✓ SERVER_PASS          Updated X minutes ago
✓ SERVER_USER          Updated X minutes ago
```

**Note**: JWT_SECRET and POSTGRES_PASSWORD are hardcoded in the workflow, not stored as secrets.

---

## 🚨 Security Best Practices

1. **Never commit secrets to Git**
   - All secrets are managed through GitHub Secrets
   - The `.env` file is auto-generated during deployment

2. **Rotate secrets regularly**
   - Change `JWT_SECRET` every 3-6 months
   - Change `POSTGRES_PASSWORD` every 6 months
   - Rotate API keys according to provider recommendations

3. **Use strong passwords**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Never use common words or patterns

4. **Limit access**
   - Only repository admins should have access to secrets
   - Review who has access regularly

5. **Monitor usage**
   - Check GitHub Actions logs for any secret leaks
   - Monitor API usage for your keys

---

## 📚 Additional Resources

- **GitHub Secrets Documentation**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **SendGrid API Keys**: https://app.sendgrid.com/settings/api_keys
- **Password Generator**: https://passwordsgenerator.net/

---

## ❓ Troubleshooting

### "Secret not found" error in workflow
- Make sure the secret name matches exactly (case-sensitive)
- Check that you added it to the correct repository
- Verify in Settings → Secrets → Actions

### Deployment fails with authentication error
- Check that `OPENAI_API_KEY` is valid
- Verify `JWT_SECRET` is set and not empty
- Confirm `POSTGRES_PASSWORD` is strong enough

### Emails not working
- Verify `SENDGRID_API_KEY` is active
- Check that `EMAIL_FROM` is verified in SendGrid
- Confirm domain authentication in SendGrid

---

## 🔄 Updating Secrets

To update a secret:
1. Go to https://github.com/Hadi-Hsn/CareConnect/settings/secrets/actions
2. Click on the secret name
3. Click "Update secret"
4. Enter the new value
5. Click "Update secret"

The next deployment will automatically use the new value!
