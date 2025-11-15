# 🚀 Complete Deployment Guide - ibhoom on Hostinger KVM2 VPS

This comprehensive guide will help you deploy your ibhoom application (frontend + backend) on a Hostinger KVM2 VPS with PostgreSQL database.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Server Setup](#initial-server-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Nginx Configuration](#nginx-configuration)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Systemd Service](#systemd-service)
9. [Firewall Configuration](#firewall-configuration)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

---

## 📋 Prerequisites

Before starting, make sure you have:

- ✅ Hostinger KVM2 VPS with root/SSH access
- ✅ Domain name pointing to your VPS IP (optional but recommended)
- ✅ Git repository URL (or code ready to upload)
- ✅ Basic knowledge of Linux commands
- ✅ SSH client (PuTTY, Terminal, or VS Code Remote SSH)

### VPS Specifications Used:
- **RAM**: 3GB
- **Storage**: 50GB
- **OS**: Ubuntu 20.04/22.04 (recommended)

---

## 🔧 Initial Server Setup

### Step 1: Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
# or
ssh root@yourdomain.com
```

### Step 2: Update System

```bash
apt-get update
apt-get upgrade -y
```

### Step 3: Install Required Packages

```bash
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
```

### Step 4: Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
```

---

## 🗄️ Database Setup

### Step 1: Start PostgreSQL

```bash
systemctl start postgresql
systemctl enable postgresql
```

### Step 2: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE ibhoom_db;
CREATE USER ibhoom_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE ibhoom_db TO ibhoom_user;

# For PostgreSQL 15+
\c ibhoom_db
GRANT ALL ON SCHEMA public TO ibhoom_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ibhoom_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ibhoom_user;

# Exit
\q
```

**Or use the automated script:**

```bash
cd /path/to/your/project/deployment
chmod +x setup-database.sh
sudo ./setup-database.sh
```

### Step 3: Optimize PostgreSQL for 3GB RAM

Edit PostgreSQL configuration:

```bash
# Find PostgreSQL version
psql --version

# Edit config (replace 14 with your version)
nano /etc/postgresql/14/main/postgresql.conf
```

Add or modify these settings:

```ini
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB
max_connections = 100
```

Restart PostgreSQL:

```bash
systemctl restart postgresql
```

---

## 🐍 Backend Deployment

### Step 1: Create Application Directory

```bash
mkdir -p /var/www/ibhoom
cd /var/www/ibhoom
```

### Step 2: Clone Your Repository

```bash
git clone https://github.com/yourusername/ibhoom.git .
# Or upload your code using SCP/SFTP
```

### Step 3: Setup Python Virtual Environment

```bash
cd /var/www/ibhoom/backend
python3.11 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Create Environment File

```bash
nano /var/www/ibhoom/backend/.env
```

Add the following configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://ibhoom_user:your_secure_password_here@localhost:5432/ibhoom_db

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here_use_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
BACKEND_CORS_ORIGINS=http://yourdomain.com,https://yourdomain.com,http://localhost:5173

# App Configuration
DEBUG=false
APP_NAME=ibhoom
APP_VERSION=1.0.0

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Cloudinary (optional - for image hosting)
# CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Firebase (optional - for push notifications)
# FIREBASE_ENABLED=false
# FIREBASE_SERVICE_ACCOUNT_PATH=/var/www/ibhoom/backend/firebase-service-account.json

# Admin Configuration
ADMIN_EMAIL=admin@ibhoom.com
ADMIN_PASSWORD=ChangeThisPassword123!
```

**Generate secure JWT secret:**

```bash
openssl rand -hex 32
```

### Step 6: Create Required Directories

```bash
mkdir -p /var/www/ibhoom/backend/uploads
mkdir -p /var/www/ibhoom/backend/static
```

### Step 7: Run Database Migrations

```bash
cd /var/www/ibhoom/backend
source venv/bin/activate
alembic upgrade head
```

### Step 8: Initialize Database

```bash
# This will create the admin user
python -c "from app.utils.init_db import init_db; init_db()"
```

### Step 9: Test Backend

```bash
# Test if backend runs
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Press `Ctrl+C` to stop. If it works, proceed to the next step.

---

## ⚛️ Frontend Deployment

### Step 1: Navigate to Frontend Directory

```bash
cd /var/www/ibhoom/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure API Endpoint

Create a `.env` file for the frontend:

```bash
cd /var/www/ibhoom/frontend
cp .env.example .env
nano .env
```

Update the API URL:

```env
VITE_API_URL=https://yourdomain.com
# or http://YOUR_VPS_IP if you don't have a domain yet
```

**Note**: The frontend uses `VITE_API_URL` environment variable. After building, the API calls will use this URL.

### Step 4: Build Frontend

```bash
npm run build
```

This creates a `dist` directory with production-ready files.

### Step 5: Set Permissions

```bash
chown -R www-data:www-data /var/www/ibhoom
chmod -R 755 /var/www/ibhoom
```

---

## 🌐 Nginx Configuration

### Step 1: Copy Nginx Configuration

```bash
cp /var/www/ibhoom/deployment/nginx/ibhoom.conf /etc/nginx/sites-available/ibhoom
```

### Step 2: Edit Configuration

```bash
nano /etc/nginx/sites-available/ibhoom
```

Update the `server_name` directive with your domain:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

### Step 3: Enable Site

```bash
# Create symlink
ln -s /etc/nginx/sites-available/ibhoom /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Reload nginx
systemctl reload nginx
```

### Step 4: Verify Nginx Status

```bash
systemctl status nginx
```

---

## 🔒 SSL Certificate Setup (Let's Encrypt)

### Step 1: Install Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

### Step 3: Auto-Renewal

Certbot automatically sets up renewal. Test it:

```bash
certbot renew --dry-run
```

### Step 4: Update Nginx Config for HTTPS

After SSL setup, uncomment the HTTPS server block in `/etc/nginx/sites-available/ibhoom` and update domain names.

---

## ⚙️ Systemd Service

### Step 1: Create Service File

```bash
cp /var/www/ibhoom/deployment/systemd/ibhoom-backend.service /etc/systemd/system/
```

### Step 2: Edit Service File (if needed)

```bash
nano /etc/systemd/system/ibhoom-backend.service
```

Make sure paths are correct:
- `WorkingDirectory=/var/www/ibhoom/backend`
- `EnvironmentFile=/var/www/ibhoom/backend/.env`
- `ExecStart=/var/www/ibhoom/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2`

### Step 3: Enable and Start Service

```bash
systemctl daemon-reload
systemctl enable ibhoom-backend
systemctl start ibhoom-backend
```

### Step 4: Check Status

```bash
systemctl status ibhoom-backend
```

### Step 5: View Logs

```bash
# View logs
journalctl -u ibhoom-backend -f

# View last 100 lines
journalctl -u ibhoom-backend -n 100
```

---

## 🔥 Firewall Configuration

### Basic Firewall Rules

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## 🧪 Testing Your Deployment

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### 2. Test Frontend

Visit `http://yourdomain.com` or `http://YOUR_VPS_IP` in your browser.

### 3. Test API

```bash
curl http://yourdomain.com/api/health
```

### 4. Check All Services

```bash
# Check PostgreSQL
systemctl status postgresql

# Check Nginx
systemctl status nginx

# Check Backend
systemctl status ibhoom-backend

# Check if backend is listening
netstat -tlnp | grep 8000
```

---

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# Check logs
journalctl -u ibhoom-backend -n 50

# Check if port is in use
netstat -tlnp | grep 8000

# Test manually
cd /var/www/ibhoom/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U ibhoom_user -d ibhoom_db -h localhost

# Check PostgreSQL status
systemctl status postgresql

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log
```

### Nginx Issues

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/ibhoom_error.log

# Check access logs
tail -f /var/log/nginx/ibhoom_access.log
```

### Permission Issues

```bash
# Fix ownership
chown -R www-data:www-data /var/www/ibhoom

# Fix permissions
chmod -R 755 /var/www/ibhoom
chmod -R 775 /var/www/ibhoom/backend/uploads
```

### Frontend Not Loading

1. Check if build was successful: `ls -la /var/www/ibhoom/frontend/dist`
2. Check Nginx configuration points to correct directory
3. Check browser console for errors
4. Verify API endpoint in frontend code

---

## 🔄 Maintenance

### Updating Your Application

```bash
# 1. Pull latest code
cd /var/www/ibhoom
git pull origin main

# 2. Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 3. Restart backend
systemctl restart ibhoom-backend

# 4. Update frontend
cd ../frontend
npm install
npm run build

# 5. Reload nginx
systemctl reload nginx
```

### Database Backups

```bash
# Create backup script
nano /usr/local/bin/backup-ibhoom-db.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ibhoom"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U ibhoom_user -d ibhoom_db > $BACKUP_DIR/ibhoom_db_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

Make executable:

```bash
chmod +x /usr/local/bin/backup-ibhoom-db.sh
```

Add to crontab (daily at 2 AM):

```bash
crontab -e
# Add:
0 2 * * * /usr/local/bin/backup-ibhoom-db.sh
```

### Monitoring

```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory
free -h

# Check running processes
ps aux | grep -E 'uvicorn|nginx|postgres'
```

### Log Rotation

Nginx and systemd handle log rotation automatically, but you can configure custom rotation:

```bash
nano /etc/logrotate.d/ibhoom
```

Add:

```
/var/log/nginx/ibhoom_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

---

## 📊 Performance Optimization

### 1. Enable Gzip Compression

Already included in Nginx config, but verify:

```bash
grep gzip /etc/nginx/sites-available/ibhoom
```

### 2. PostgreSQL Tuning

Already configured for 3GB RAM, but you can fine-tune based on usage.

### 3. Backend Workers

Adjust workers in systemd service based on CPU cores:

```bash
# For 2 CPU cores, use 2-4 workers
--workers 2
```

### 4. Enable Caching

Nginx config includes caching for static assets. Consider adding Redis for API caching if needed.

---

## 🔐 Security Checklist

- [ ] Changed default admin password
- [ ] Set strong JWT_SECRET_KEY
- [ ] Configured CORS properly
- [ ] Enabled firewall (UFW)
- [ ] SSL certificate installed
- [ ] Database user has limited privileges
- [ ] DEBUG=false in production
- [ ] Regular backups configured
- [ ] Updated system packages
- [ ] Strong database password

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: Always check logs first
   ```bash
   journalctl -u ibhoom-backend -f
   tail -f /var/log/nginx/ibhoom_error.log
   ```

2. **Verify Services**: Make sure all services are running
   ```bash
   systemctl status ibhoom-backend nginx postgresql
   ```

3. **Test Manually**: Try running components manually to isolate issues

4. **Check Configuration**: Verify all config files are correct

---

## 🎉 Success!

Your ibhoom application should now be live at:
- **Frontend**: `https://yourdomain.com`
- **Backend API**: `https://yourdomain.com/api`
- **API Docs**: `https://yourdomain.com/docs`

**Next Steps:**
1. Test all functionality
2. Set up monitoring
3. Configure backups
4. Update DNS if needed
5. Share your application! 🚀

---

**Last Updated**: 2024
**Version**: 1.0

