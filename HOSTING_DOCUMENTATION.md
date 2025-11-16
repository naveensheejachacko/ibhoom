# 🚀 ibhoom Hosting Documentation

Complete documentation for hosting ibhoom application on Hostinger VPS with Cloudflare.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Infrastructure Details](#infrastructure-details)
3. [Domain Configuration](#domain-configuration)
4. [Server Setup](#server-setup)
5. [Application Deployment](#application-deployment)
6. [Configuration Files](#configuration-files)
7. [Services Management](#services-management)
8. [Maintenance & Updates](#maintenance--updates)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)
11. [Backup & Recovery](#backup--recovery)
12. [Monitoring](#monitoring)

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────┐
│              Cloudflare CDN                      │
│  - SSL/TLS Termination                           │
│  - DDoS Protection                               │
│  - CDN Caching                                   │
└──────────────┬──────────────────────────────────┘
               │
               │ HTTPS (443)
               │
┌──────────────▼──────────────────────────────────┐
│         Hostinger VPS (KVM2)                     │
│  ┌──────────────────────────────────────────┐  │
│  │         Nginx (Port 80)                   │  │
│  │  - Frontend: ibhoom.in                    │  │
│  │  - Backend API: api.ibhoom.in            │  │
│  └──────┬───────────────────┬────────────────┘  │
│         │                   │                    │
│  ┌──────▼──────┐    ┌──────▼──────┐            │
│  │   React     │    │   FastAPI    │            │
│  │  Frontend   │    │   Backend    │            │
│  │  (Static)   │    │  (Port 8000) │            │
│  └─────────────┘    └──────┬──────┘            │
│                             │                    │
│                      ┌──────▼──────┐            │
│                      │ PostgreSQL  │            │
│                      │  Database   │            │
│                      │  (Port 5432)│            │
│                      └─────────────┘            │
└─────────────────────────────────────────────────┘
```

### Domain Structure

- **Frontend**: `https://ibhoom.in` → Serves React application
- **Backend API**: `https://api.ibhoom.in` → FastAPI backend
- **WWW**: `https://www.ibhoom.in` → Redirects to main domain

---

## 🖥️ Infrastructure Details

### VPS Specifications

- **Provider**: Hostinger
- **Type**: KVM2 VPS
- **RAM**: 3GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS
- **IP Address**: `88.222.242.64` (IPv4)

### Software Stack

- **Web Server**: Nginx 1.24.0
- **Backend**: FastAPI (Python 3.12)
- **Frontend**: React + Vite
- **Database**: PostgreSQL 14+
- **Process Manager**: systemd
- **Reverse Proxy**: Cloudflare

### Resource Allocation

```
System & OS:          ~500MB - 1GB
PostgreSQL:           ~512MB - 1GB
FastAPI Backend:      ~100MB - 300MB
Nginx:                ~10MB - 20MB
React Frontend:       ~0MB (static files)
Buffer/Swap:          ~500MB

Total Estimated:      ~1.6GB - 2.8GB ✅
```

---

## 🌐 Domain Configuration

### Cloudflare Setup

#### DNS Records

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | `@` | `88.222.242.64` | 🟠 Proxied | Auto |
| A | `api` | `88.222.242.64` | 🟠 Proxied | Auto |
| CNAME | `www` | `ibhoom.in` | 🟠 Proxied | Auto |

#### SSL/TLS Configuration

- **Encryption Mode**: Flexible
- **Always Use HTTPS**: Enabled
- **Minimum TLS Version**: TLS 1.2
- **Automatic HTTPS Rewrites**: Enabled

#### Nameservers

- `heidi.ns.cloudflare.com`
- `austin.ns.cloudflare.com`

**Note**: Nameservers are configured at GoDaddy domain registrar.

### Domain Registrar (GoDaddy)

- **Domain**: `ibhoom.in`
- **Nameservers**: Cloudflare nameservers (configured)
- **DNS Management**: Handled by Cloudflare

---

## 🖥️ Server Setup

### Server Access

```bash
# SSH Access
ssh root@88.222.242.64
# or
ssh root@ibhoom.in
```

### Directory Structure

```
/var/www/ibhoom/
├── backend/
│   ├── app/              # FastAPI application
│   ├── migrations/       # Alembic migrations
│   ├── venv/             # Python virtual environment
│   ├── .env              # Backend environment variables
│   ├── requirements.txt  # Python dependencies
│   └── alembic.ini       # Alembic configuration
├── frontend/
│   ├── src/              # React source code
│   ├── dist/             # Built production files
│   ├── .env              # Frontend environment variables
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration
└── deployment/           # Deployment scripts and configs
```

### File Permissions

```bash
# Application files
sudo chown -R www-data:www-data /var/www/ibhoom

# Backend uploads directory
sudo chmod -R 775 /var/www/ibhoom/backend/uploads

# Environment files
sudo chmod 600 /var/www/ibhoom/backend/.env
sudo chmod 600 /var/www/ibhoom/frontend/.env
```

---

## 📦 Application Deployment

### Initial Deployment Steps

#### 1. Clone Repository

```bash
cd /var/www
sudo git clone git@github.com:naveensheejachacko/ibhoom.git
sudo chown -R www-data:www-data /var/www/ibhoom
```

#### 2. Backend Setup

```bash
cd /var/www/ibhoom/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set ownership
sudo chown -R www-data:www-data venv
```

#### 3. Database Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE ibhoom_db;
CREATE USER ibhoom_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ibhoom_db TO ibhoom_user;
\c ibhoom_db
GRANT ALL ON SCHEMA public TO ibhoom_user;
\q
```

#### 4. Backend Configuration

```bash
cd /var/www/ibhoom/backend
sudo nano .env
```

**Required Environment Variables:**

```env
# Database (URL-encode special characters in password)
DATABASE_URL=postgresql://ibhoom_user:password@localhost:5432/ibhoom_db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
BACKEND_CORS_ORIGINS=https://ibhoom.in,https://www.ibhoom.in,http://localhost:3000

# App Configuration
DEBUG=false
APP_NAME=ibhoom
APP_VERSION=1.0.0

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Admin Configuration
ADMIN_EMAIL=admin@ibhoom.in
ADMIN_PASSWORD=secure_password_here
```

**Important**: If password contains special characters (`@`, `+`, `#`, etc.), URL-encode them:
- `@` → `%40`
- `+` → `%2B`
- `#` → `%23`

#### 5. Run Database Migrations

```bash
cd /var/www/ibhoom/backend
source venv/bin/activate
alembic upgrade head
```

#### 6. Initialize Database

```bash
python -c "from app.utils.init_db import init_db; init_db()"
```

#### 7. Frontend Setup

```bash
cd /var/www/ibhoom/frontend

# Install dependencies
npm install

# Create .env file
sudo nano .env
```

**Frontend Environment Variables:**

```env
VITE_API_URL=https://api.ibhoom.in
```

#### 8. Build Frontend

```bash
# Build as www-data to ensure proper ownership
sudo chown -R www-data:www-data /var/www/ibhoom/frontend
sudo -u www-data npm run build
```

---

## ⚙️ Configuration Files

### Nginx Configuration

#### Frontend Config: `/etc/nginx/sites-available/ibhoom-frontend`

```nginx
server {
    listen 80;
    server_name ibhoom.in www.ibhoom.in;
    
    root /var/www/ibhoom/frontend/dist;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend - React app
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Don't cache HTML files
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-store, no-cache, must-revalidate";
    }
    
    # Logging
    access_log /var/log/nginx/ibhoom_frontend_access.log;
    error_log /var/log/nginx/ibhoom_frontend_error.log;
}
```

#### Backend Config: `/etc/nginx/sites-available/ibhoom-backend`

```nginx
upstream backend {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name api.ibhoom.in;
    
    client_max_body_size 10M;
    
    # Backend API
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
    
    # Logging
    access_log /var/log/nginx/ibhoom_backend_access.log;
    error_log /var/log/nginx/ibhoom_backend_error.log;
}
```

### Systemd Service: `/etc/systemd/system/ibhoom-backend.service`

```ini
[Unit]
Description=ibhoom FastAPI Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/ibhoom/backend
Environment="PATH=/var/www/ibhoom/backend/venv/bin"
EnvironmentFile=/var/www/ibhoom/backend/.env
ExecStart=/var/www/ibhoom/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## 🔧 Services Management

### Service Commands

```bash
# Backend Service
sudo systemctl status ibhoom-backend
sudo systemctl start ibhoom-backend
sudo systemctl stop ibhoom-backend
sudo systemctl restart ibhoom-backend
sudo systemctl enable ibhoom-backend    # Auto-start on boot
sudo systemctl disable ibhoom-backend   # Disable auto-start

# Nginx Service
sudo systemctl status nginx
sudo systemctl restart nginx
sudo systemctl reload nginx              # Reload config without downtime
sudo nginx -t                             # Test configuration

# PostgreSQL Service
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

### View Logs

```bash
# Backend logs
sudo journalctl -u ibhoom-backend -f
sudo journalctl -u ibhoom-backend -n 50

# Nginx logs
sudo tail -f /var/log/nginx/ibhoom_frontend_error.log
sudo tail -f /var/log/nginx/ibhoom_backend_error.log
sudo tail -f /var/log/nginx/ibhoom_frontend_access.log
sudo tail -f /var/log/nginx/ibhoom_backend_access.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## 🔄 Maintenance & Updates

### Update Application Code

```bash
cd /var/www/ibhoom

# Pull latest changes
sudo git pull origin main

# Backend updates
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart ibhoom-backend

# Frontend updates
cd ../frontend
sudo -u www-data npm install
sudo -u www-data npm run build
sudo systemctl reload nginx
```

### Update System Packages

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Node.js (if needed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Database Migrations

```bash
cd /var/www/ibhoom/backend
source venv/bin/activate

# Check current migration
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Rebuild Frontend

```bash
cd /var/www/ibhoom/frontend
sudo rm -rf dist
sudo -u www-data npm run build
sudo systemctl reload nginx
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Backend Not Starting

```bash
# Check service status
sudo systemctl status ibhoom-backend

# Check logs
sudo journalctl -u ibhoom-backend -n 50

# Test manually
cd /var/www/ibhoom/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Common Causes:**
- Missing `.env` file
- Database connection error
- Port 8000 already in use
- Permission issues

#### 2. Frontend Not Loading

```bash
# Check if dist folder exists
ls -la /var/www/ibhoom/frontend/dist/

# Check Nginx config
sudo nginx -t

# Check Nginx error logs
sudo tail -f /var/log/nginx/ibhoom_frontend_error.log

# Test directly
curl -H "Host: ibhoom.in" http://localhost/
```

**Common Causes:**
- Frontend not built
- Wrong Nginx root path
- Permission issues
- Cloudflare SSL mode incorrect

#### 3. Database Connection Errors

```bash
# Test database connection
sudo -u postgres psql -d ibhoom_db -U ibhoom_user

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep ibhoom
```

**Common Causes:**
- Wrong password (check URL encoding)
- Database doesn't exist
- PostgreSQL not running
- Wrong connection string format

#### 4. Cloudflare 521 Error

**Symptoms**: `Error 521: Web server is down`

**Solutions:**
1. Check Cloudflare SSL mode is "Flexible"
2. Verify DNS A record points to correct IP
3. Check if server is accessible: `curl http://YOUR_VPS_IP`
4. Verify Nginx is running: `sudo systemctl status nginx`
5. Check firewall: `sudo ufw status`

#### 5. Permission Denied Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ibhoom

# Fix permissions
sudo chmod -R 755 /var/www/ibhoom
sudo chmod 600 /var/www/ibhoom/backend/.env
sudo chmod 775 /var/www/ibhoom/backend/uploads
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health
curl https://api.ibhoom.in/health

# Frontend
curl -I https://ibhoom.in

# Database
sudo -u postgres psql -d ibhoom_db -c "SELECT 1;"
```

---

## 🔒 Security Best Practices

### 1. Firewall Configuration

```bash
# Check firewall status
sudo ufw status

# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. SSH Security

```bash
# Disable root login (create sudo user first)
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Use SSH keys instead of passwords
# Disable password authentication
# Set: PasswordAuthentication no
```

### 3. Environment Variables

- Never commit `.env` files to git
- Use strong, random JWT secrets
- URL-encode special characters in passwords
- Restrict file permissions: `chmod 600 .env`

### 4. Database Security

```bash
# Use strong passwords
# Limit database user privileges
# Regular backups
# Keep PostgreSQL updated
```

### 5. Cloudflare Security

- Enable "Always Use HTTPS"
- Enable "Automatic HTTPS Rewrites"
- Use "Flexible" SSL mode (or "Full" with server SSL)
- Enable DDoS protection
- Configure WAF rules if needed

### 6. Application Security

- Set `DEBUG=false` in production
- Use strong CORS origins
- Validate all inputs
- Keep dependencies updated
- Regular security audits: `npm audit`, `pip check`

---

## 💾 Backup & Recovery

### Database Backup

```bash
# Create backup
sudo -u postgres pg_dump ibhoom_db > /var/backups/ibhoom_db_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
sudo -u postgres pg_dump ibhoom_db | gzip > /var/backups/ibhoom_db_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore backup
sudo -u postgres psql ibhoom_db < /var/backups/ibhoom_db_YYYYMMDD.sql
```

### Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-ibhoom.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ibhoom"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump ibhoom_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/ibhoom

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-ibhoom.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ibhoom.sh
```

### File Backups

```bash
# Backup uploads
tar -czf /var/backups/uploads_$(date +%Y%m%d).tar.gz /var/www/ibhoom/backend/uploads

# Backup .env files (store securely!)
sudo cp /var/www/ibhoom/backend/.env /var/backups/backend.env
sudo cp /var/www/ibhoom/frontend/.env /var/backups/frontend.env
```

---

## 📊 Monitoring

### System Monitoring

```bash
# CPU and Memory
htop
# or
top

# Disk usage
df -h
du -sh /var/www/ibhoom/*

# Network
sudo netstat -tulpn
sudo ss -tulpn
```

### Application Monitoring

```bash
# Service status
sudo systemctl status ibhoom-backend nginx postgresql

# Check if services are running
sudo systemctl is-active ibhoom-backend
sudo systemctl is-active nginx
sudo systemctl is-active postgresql

# Resource usage
sudo systemctl status ibhoom-backend | grep Memory
```

### Log Monitoring

```bash
# Real-time log monitoring
sudo journalctl -u ibhoom-backend -f
sudo tail -f /var/log/nginx/ibhoom_backend_error.log

# Check for errors
sudo journalctl -u ibhoom-backend -p err
sudo grep -i error /var/log/nginx/ibhoom_backend_error.log
```

### Uptime Monitoring

Consider using external monitoring services:
- UptimeRobot
- Pingdom
- StatusCake

Monitor endpoints:
- `https://ibhoom.in`
- `https://api.ibhoom.in/health`

---

## 📝 Quick Reference

### Important Paths

```
Application:     /var/www/ibhoom
Backend:         /var/www/ibhoom/backend
Frontend:        /var/www/ibhoom/frontend
Nginx Configs:   /etc/nginx/sites-available/
Service File:    /etc/systemd/system/ibhoom-backend.service
Logs:            /var/log/nginx/
Database:        PostgreSQL (localhost:5432)
```

### Important Commands

```bash
# Restart everything
sudo systemctl restart ibhoom-backend nginx

# View logs
sudo journalctl -u ibhoom-backend -f

# Test Nginx
sudo nginx -t && sudo systemctl reload nginx

# Check services
sudo systemctl status ibhoom-backend nginx postgresql

# Database access
sudo -u postgres psql -d ibhoom_db
```

### Environment URLs

- **Frontend**: https://ibhoom.in
- **Backend API**: https://api.ibhoom.in
- **API Docs**: https://api.ibhoom.in/docs
- **Health Check**: https://api.ibhoom.in/health

---

## 📞 Support & Resources

### Documentation

- [Hostinger VPS Deployment Guide](HOSTINGER_VPS_DEPLOYMENT.md)
- [Cloudflare Domain Setup](CLOUDFLARE_DOMAIN_SETUP.md)
- [Alembic Migrations Guide](ALEMBIC_MIGRATIONS_GUIDE.md)

### External Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Cloudflare Documentation](https://developers.cloudflare.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Contact Information

- **Repository**: https://github.com/naveensheejachacko/ibhoom
- **VPS Provider**: Hostinger
- **Domain Registrar**: GoDaddy
- **CDN**: Cloudflare

---

## ✅ Deployment Checklist

### Initial Setup

- [ ] VPS provisioned and accessible
- [ ] Domain registered and configured
- [ ] Cloudflare account created
- [ ] DNS records configured
- [ ] SSL/TLS configured
- [ ] Server packages installed
- [ ] Database created
- [ ] Application cloned
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Migrations run
- [ ] Frontend built
- [ ] Nginx configured
- [ ] Services started
- [ ] Firewall configured
- [ ] Backups configured

### Post-Deployment

- [ ] All endpoints tested
- [ ] SSL certificates working
- [ ] Monitoring set up
- [ ] Backups tested
- [ ] Documentation updated
- [ ] Team access configured

---

**Last Updated**: November 16, 2025  
**Version**: 1.0.0  
**Maintained By**: ibhoom Development Team

