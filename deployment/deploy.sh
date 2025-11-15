#!/bin/bash

# Deployment script for ibhoom on Hostinger KVM2 VPS
# This script automates the deployment process
# Run as root or with sudo

set -e

echo "🚀 Starting ibhoom deployment on Hostinger VPS..."

# Configuration
APP_DIR="/var/www/ibhoom"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
REPO_URL=""  # Set your Git repository URL here
DOMAIN=""    # Set your domain name here (optional)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    certbot \
    python3-certbot-nginx \
    ufw

# Create application directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$BACKEND_DIR"
mkdir -p "$FRONTEND_DIR"
mkdir -p "$BACKEND_DIR/uploads"
mkdir -p "$BACKEND_DIR/static"

# Set permissions
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"

# Clone repository (if REPO_URL is set)
if [ -n "$REPO_URL" ]; then
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    cd "$APP_DIR"
    git clone "$REPO_URL" .
else
    echo -e "${YELLOW}⚠️  REPO_URL not set. Please clone your repository manually to $APP_DIR${NC}"
    echo "   Example: git clone https://github.com/yourusername/ibhoom.git $APP_DIR"
    read -p "Press Enter after you've cloned the repository..."
fi

# Setup Backend
echo -e "${YELLOW}🐍 Setting up Python backend...${NC}"
cd "$BACKEND_DIR"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > "$BACKEND_DIR/.env" << EOF
# Database Configuration
DATABASE_URL=postgresql://ibhoom_user:YOUR_PASSWORD_HERE@localhost:5432/ibhoom_db

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost,http://127.0.0.1
# Add your domain: BACKEND_CORS_ORIGINS=http://yourdomain.com,https://yourdomain.com

# App Configuration
DEBUG=false
APP_NAME=ibhoom
APP_VERSION=1.0.0

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Cloudinary (optional)
# CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Firebase (optional)
# FIREBASE_ENABLED=false
# FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/service-account.json

# Admin Configuration
ADMIN_EMAIL=admin@ibhoom.com
ADMIN_PASSWORD=ChangeThisPassword123!
EOF
    echo -e "${GREEN}✅ .env file created. Please edit it with your database password and other settings.${NC}"
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
source venv/bin/activate
alembic upgrade head

# Setup Frontend
echo -e "${YELLOW}⚛️  Setting up React frontend...${NC}"
cd "$FRONTEND_DIR"

# Install Node.js dependencies
npm install

# Build frontend
echo -e "${YELLOW}🏗️  Building frontend...${NC}"
npm run build

# Setup Nginx
echo -e "${YELLOW}🌐 Setting up Nginx...${NC}"
if [ -f "$APP_DIR/deployment/nginx/ibhoom.conf" ]; then
    cp "$APP_DIR/deployment/nginx/ibhoom.conf" /etc/nginx/sites-available/ibhoom
    
    # Update domain in nginx config if provided
    if [ -n "$DOMAIN" ]; then
        sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/ibhoom
    fi
    
    # Enable site
    ln -sf /etc/nginx/sites-available/ibhoom /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    # Reload nginx
    systemctl reload nginx
else
    echo -e "${RED}❌ Nginx config file not found at $APP_DIR/deployment/nginx/ibhoom.conf${NC}"
fi

# Setup systemd service
echo -e "${YELLOW}⚙️  Setting up systemd service...${NC}"
if [ -f "$APP_DIR/deployment/systemd/ibhoom-backend.service" ]; then
    cp "$APP_DIR/deployment/systemd/ibhoom-backend.service" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable ibhoom-backend
    systemctl start ibhoom-backend
else
    echo -e "${RED}❌ Systemd service file not found${NC}"
fi

# Setup firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable

# Final instructions
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit $BACKEND_DIR/.env with your database password and settings"
echo "2. Update CORS origins in .env file with your domain"
echo "3. Restart the backend: sudo systemctl restart ibhoom-backend"
echo "4. Check backend status: sudo systemctl status ibhoom-backend"
echo "5. Check nginx status: sudo systemctl status nginx"
echo "6. View backend logs: sudo journalctl -u ibhoom-backend -f"
echo ""
if [ -n "$DOMAIN" ]; then
    echo "7. Setup SSL certificate: sudo certbot --nginx -d $DOMAIN"
else
    echo "7. Setup SSL certificate: sudo certbot --nginx -d yourdomain.com"
fi
echo ""
echo "🌐 Your application should be accessible at:"
if [ -n "$DOMAIN" ]; then
    echo "   http://$DOMAIN (or https://$DOMAIN after SSL setup)"
else
    echo "   http://YOUR_SERVER_IP (replace with your actual IP)"
fi
echo ""
