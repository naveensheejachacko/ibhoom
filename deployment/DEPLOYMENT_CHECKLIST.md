# ✅ Deployment Checklist - ibhoom on Hostinger VPS

Use this checklist to ensure you complete all deployment steps correctly.

## 📋 Pre-Deployment

- [ ] VPS access (SSH credentials)
- [ ] Domain name configured (optional)
- [ ] Git repository URL ready
- [ ] Read `HOSTINGER_VPS_DEPLOYMENT.md`

## 🔧 Server Setup

- [ ] Connected to VPS via SSH
- [ ] System updated (`apt-get update && apt-get upgrade`)
- [ ] Required packages installed (Python, Node.js, PostgreSQL, Nginx)
- [ ] Firewall configured (UFW)

## 🗄️ Database Setup

- [ ] PostgreSQL installed and running
- [ ] Database created (`ibhoom_db`)
- [ ] Database user created (`ibhoom_user`)
- [ ] Password set and saved securely
- [ ] Permissions granted
- [ ] PostgreSQL optimized for 3GB RAM
- [ ] Tested database connection

## 🐍 Backend Setup

- [ ] Application directory created (`/var/www/ibhoom`)
- [ ] Code cloned/uploaded to server
- [ ] Python virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with:
  - [ ] `DATABASE_URL` configured
  - [ ] `JWT_SECRET_KEY` set (strong random value)
  - [ ] `BACKEND_CORS_ORIGINS` configured
  - [ ] `DEBUG=false`
  - [ ] Other required variables
- [ ] Upload directories created (`uploads/`, `static/`)
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Database initialized (admin user created)
- [ ] Backend tested manually

## ⚛️ Frontend Setup

- [ ] Frontend dependencies installed (`npm install`)
- [ ] `.env` file created with `VITE_API_URL`
- [ ] API URL points to production backend
- [ ] Frontend built (`npm run build`)
- [ ] Build output verified (`dist/` directory exists)
- [ ] Permissions set correctly

## 🌐 Nginx Configuration

- [ ] Nginx config file copied to `/etc/nginx/sites-available/`
- [ ] Domain name updated in config (if using domain)
- [ ] Site enabled (symlink created)
- [ ] Default site removed
- [ ] Nginx config tested (`nginx -t`)
- [ ] Nginx reloaded/restarted
- [ ] Nginx status verified

## ⚙️ Systemd Service

- [ ] Service file copied to `/etc/systemd/system/`
- [ ] Paths verified in service file
- [ ] Systemd daemon reloaded
- [ ] Service enabled (auto-start on boot)
- [ ] Service started
- [ ] Service status checked (active/running)
- [ ] Logs reviewed (no errors)

## 🔒 SSL Certificate (Optional but Recommended)

- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] HTTPS server block configured in Nginx
- [ ] HTTP to HTTPS redirect enabled
- [ ] Auto-renewal tested
- [ ] SSL certificate verified

## ✅ Testing

- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend accessible: Visit `http://yourdomain.com` or IP
- [ ] API accessible: `curl http://yourdomain.com/api/health`
- [ ] API docs accessible: Visit `/docs` endpoint
- [ ] Login functionality tested
- [ ] Database operations tested
- [ ] File uploads tested (if applicable)

## 🔐 Security

- [ ] Admin password changed from default
- [ ] Strong JWT secret key set
- [ ] CORS origins configured correctly
- [ ] DEBUG mode disabled
- [ ] Firewall enabled and configured
- [ ] SSL certificate installed (if using domain)
- [ ] File permissions set correctly
- [ ] Database user has limited privileges

## 📊 Monitoring & Maintenance

- [ ] Service status commands tested
- [ ] Log viewing commands tested
- [ ] Backup script created (if needed)
- [ ] Cron job for backups configured (if needed)
- [ ] Update procedure documented
- [ ] Monitoring setup (optional)

## 🎯 Post-Deployment

- [ ] All functionality tested
- [ ] Performance checked
- [ ] Error logs reviewed
- [ ] Documentation updated
- [ ] Team notified (if applicable)
- [ ] DNS records updated (if applicable)

## 📝 Notes

Document any custom configurations or issues encountered:

```
Date: ___________
Deployed by: ___________
Domain/IP: ___________
Database password location: ___________
JWT secret location: ___________
Custom configurations:
_______________________________________
_______________________________________
_______________________________________
```

## 🆘 Troubleshooting Log

If issues occurred, document them here:

```
Issue: ________________________________
Solution: _____________________________
_______________________________________
```

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Status**: ⬜ In Progress | ⬜ Complete | ⬜ Failed

---

For detailed instructions, see `HOSTINGER_VPS_DEPLOYMENT.md`
For quick reference, see `QUICK_START.md`

