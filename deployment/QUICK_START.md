# 🚀 Quick Start Guide - Hostinger VPS Deployment

This is a condensed guide for deploying ibhoom on Hostinger KVM2 VPS. For detailed instructions, see [HOSTINGER_VPS_DEPLOYMENT.md](../HOSTINGER_VPS_DEPLOYMENT.md).

## ⚡ Quick Deployment (Automated)

### Option 1: Use the Automated Script

```bash
# 1. Connect to your VPS
ssh root@YOUR_VPS_IP

# 2. Clone your repository
cd /var/www
git clone https://github.com/yourusername/ibhoom.git ibhoom

# 3. Run the deployment script
cd ibhoom/deployment
chmod +x deploy.sh setup-database.sh
sudo ./setup-database.sh  # Setup database first
sudo ./deploy.sh          # Deploy everything

# 4. Edit .env file with your database password
nano /var/www/ibhoom/backend/.env

# 5. Restart services
sudo systemctl restart ibhoom-backend
sudo systemctl reload nginx
```

## 📝 Manual Deployment Steps

### 1. Setup Database

```bash
sudo -u postgres psql
CREATE DATABASE ibhoom_db;
CREATE USER ibhoom_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ibhoom_db TO ibhoom_user;
\c ibhoom_db
GRANT ALL ON SCHEMA public TO ibhoom_user;
\q
```

### 2. Setup Backend

```bash
cd /var/www/ibhoom/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env  # Add DATABASE_URL and other configs

# Run migrations
alembic upgrade head
```

### 3. Setup Frontend

```bash
cd /var/www/ibhoom/frontend
npm install
npm run build
```

### 4. Setup Nginx

```bash
sudo cp /var/www/ibhoom/deployment/nginx/ibhoom.conf /etc/nginx/sites-available/ibhoom
sudo ln -s /etc/nginx/sites-available/ibhoom /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Setup Systemd Service

```bash
sudo cp /var/www/ibhoom/deployment/systemd/ibhoom-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ibhoom-backend
sudo systemctl start ibhoom-backend
```

### 6. Setup SSL (Optional but Recommended)

```bash
sudo certbot --nginx -d yourdomain.com
```

## ✅ Verification

```bash
# Check all services
sudo systemctl status ibhoom-backend
sudo systemctl status nginx
sudo systemctl status postgresql

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost/
```

## 🔧 Common Commands

```bash
# View backend logs
sudo journalctl -u ibhoom-backend -f

# Restart backend
sudo systemctl restart ibhoom-backend

# Restart nginx
sudo systemctl restart nginx

# Update application
cd /var/www/ibhoom
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt && alembic upgrade head
cd ../frontend && npm install && npm run build
sudo systemctl restart ibhoom-backend
sudo systemctl reload nginx
```

## 📋 Required Environment Variables

Create `/var/www/ibhoom/backend/.env`:

```env
DATABASE_URL=postgresql://ibhoom_user:password@localhost:5432/ibhoom_db
JWT_SECRET_KEY=your_secret_key_here
BACKEND_CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

## 🆘 Troubleshooting

- **Backend not starting**: Check logs with `journalctl -u ibhoom-backend -n 50`
- **Database connection error**: Verify DATABASE_URL in .env file
- **Frontend not loading**: Check nginx config and build output
- **Permission errors**: Run `sudo chown -R www-data:www-data /var/www/ibhoom`

For detailed troubleshooting, see [HOSTINGER_VPS_DEPLOYMENT.md](../HOSTINGER_VPS_DEPLOYMENT.md).

