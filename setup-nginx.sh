#!/bin/bash
# Setup script for carecon.online on Ubuntu/Debian server

set -e

echo "=== Setting up carecon.online ==="

# Install required packages
echo "Installing required packages..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Copy nginx configuration
echo "Setting up Nginx configuration..."
cp nginx-server.conf /etc/nginx/sites-available/carecon.online
ln -sf /etc/nginx/sites-available/carecon.online /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Restart nginx
echo "Restarting Nginx..."
systemctl restart nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate from Let's Encrypt..."
certbot --nginx -d carecon.online -d www.carecon.online --non-interactive --agree-tos --email hadihacan@gmail.com --redirect

# Enable certbot auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

# Restart nginx with SSL
systemctl restart nginx

echo "=== Setup complete! ==="
echo "Your site should now be available at:"
echo "  https://carecon.online"
echo ""
echo "Make sure your DNS points to this server:"
echo "  A Record: carecon.online -> 46.62.253.61"
echo "  A Record: www.carecon.online -> 46.62.253.61"
