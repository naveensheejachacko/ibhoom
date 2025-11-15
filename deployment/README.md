# 📦 Deployment Files

This directory contains all the necessary files and scripts for deploying ibhoom on a Hostinger KVM2 VPS.

## 📁 Directory Structure

```
deployment/
├── nginx/
│   └── ibhoom.conf          # Nginx configuration for frontend and backend
├── systemd/
│   └── ibhoom-backend.service  # Systemd service file for FastAPI backend
├── deploy.sh                # Automated deployment script
├── setup-database.sh         # PostgreSQL database setup script
├── QUICK_START.md           # Quick reference guide
└── README.md                # This file
```

## 🚀 Quick Start

1. **Read the comprehensive guide**: [HOSTINGER_VPS_DEPLOYMENT.md](../HOSTINGER_VPS_DEPLOYMENT.md)
2. **Or use the quick start**: [QUICK_START.md](QUICK_START.md)
3. **Run automated scripts**: See instructions below

## 📋 Files Description

### Nginx Configuration (`nginx/ibhoom.conf`)

- Serves React frontend static files
- Proxies API requests to FastAPI backend
- Includes rate limiting and security headers
- Configured for HTTP and HTTPS (SSL)
- Gzip compression enabled

**Usage:**
```bash
sudo cp deployment/nginx/ibhoom.conf /etc/nginx/sites-available/ibhoom
sudo ln -s /etc/nginx/sites-available/ibhoom /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd Service (`systemd/ibhoom-backend.service`)

- Manages FastAPI backend as a system service
- Auto-starts on boot
- Auto-restarts on failure
- Runs with proper user permissions

**Usage:**
```bash
sudo cp deployment/systemd/ibhoom-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ibhoom-backend
sudo systemctl start ibhoom-backend
```

### Database Setup Script (`setup-database.sh`)

- Creates PostgreSQL database and user
- Configures PostgreSQL for 3GB RAM server
- Generates secure password
- Sets up proper permissions

**Usage:**
```bash
chmod +x deployment/setup-database.sh
sudo ./deployment/setup-database.sh
```

### Deployment Script (`deploy.sh`)

- Automated deployment script
- Installs all dependencies
- Sets up backend and frontend
- Configures Nginx and systemd
- Sets up firewall

**Usage:**
```bash
# Edit the script first to set REPO_URL and DOMAIN
nano deployment/deploy.sh

# Make executable and run
chmod +x deployment/deploy.sh
sudo ./deployment/deploy.sh
```

## ⚙️ Configuration

### Backend Environment Variables

Create `/var/www/ibhoom/backend/.env`:

```env
DATABASE_URL=postgresql://ibhoom_user:password@localhost:5432/ibhoom_db
JWT_SECRET_KEY=your_secret_key
BACKEND_CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

### Frontend Environment Variables

Create `/var/www/ibhoom/frontend/.env`:

```env
VITE_API_URL=https://yourdomain.com
```

## 🔧 Manual Setup Steps

If you prefer manual setup:

1. **Database**: Run `setup-database.sh` or follow manual steps in deployment guide
2. **Backend**: 
   - Create virtual environment
   - Install dependencies
   - Create .env file
   - Run migrations
3. **Frontend**:
   - Install dependencies
   - Create .env file
   - Build production files
4. **Nginx**: Copy and configure nginx config
5. **Systemd**: Copy and enable service file

## 📚 Documentation

- **Full Guide**: [HOSTINGER_VPS_DEPLOYMENT.md](../HOSTINGER_VPS_DEPLOYMENT.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **FAQ**: [HOSTINGER_VPS_FAQ.md](../HOSTINGER_VPS_FAQ.md)

## 🆘 Troubleshooting

### Check Service Status

```bash
sudo systemctl status ibhoom-backend
sudo systemctl status nginx
sudo systemctl status postgresql
```

### View Logs

```bash
# Backend logs
sudo journalctl -u ibhoom-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/ibhoom_error.log
sudo tail -f /var/log/nginx/ibhoom_access.log
```

### Test Configuration

```bash
# Test Nginx config
sudo nginx -t

# Test backend manually
cd /var/www/ibhoom/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 🔒 Security Notes

- Always use strong passwords
- Keep JWT_SECRET_KEY secret and random
- Enable SSL/HTTPS in production
- Keep system packages updated
- Configure firewall properly
- Set DEBUG=false in production

## 📝 Notes

- All scripts assume Ubuntu/Debian-based system
- Paths assume application is in `/var/www/ibhoom`
- Scripts use `www-data` user for web services
- PostgreSQL is configured for 3GB RAM server

## 🎯 Next Steps

After deployment:

1. ✅ Test all functionality
2. ✅ Setup SSL certificate (Let's Encrypt)
3. ✅ Configure backups
4. ✅ Setup monitoring
5. ✅ Update DNS records

For detailed instructions, see [HOSTINGER_VPS_DEPLOYMENT.md](../HOSTINGER_VPS_DEPLOYMENT.md).
