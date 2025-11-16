# 🔐 ibhoom Credentials & Configuration Template

**⚠️ IMPORTANT: This is a template file. Never commit actual credentials to Git!**

Store actual credentials securely (password manager, secure vault, etc.)

---

## 📋 Credentials Checklist

### Server Access

- [ ] VPS SSH Root Password
- [ ] VPS IP Address
- [ ] SSH Key (if using key-based auth)
- [ ] Hostinger Account Credentials

### Domain & DNS

- [ ] Domain Name: `ibhoom.in`
- [ ] GoDaddy Account Credentials
- [ ] Cloudflare Account Credentials
- [ ] Cloudflare API Token (if using API)

### Database

- [ ] PostgreSQL Database Name: `ibhoom_db`
- [ ] PostgreSQL Username: `ibhoom_user`
- [ ] PostgreSQL Password: `********`
- [ ] Database Host: `localhost`
- [ ] Database Port: `5432`

**Connection String Format:**
```
postgresql://ibhoom_user:PASSWORD@localhost:5432/ibhoom_db
```

**Note**: URL-encode special characters in password:
- `@` → `%40`
- `+` → `%2B`
- `#` → `%23`
- `%` → `%25`

### Backend Environment Variables

**Location**: `/var/www/ibhoom/backend/.env`

```env
# Database Configuration
DATABASE_URL=postgresql://ibhoom_user:PASSWORD@localhost:5432/ibhoom_db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

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

# Cloudinary (Optional)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Firebase (Optional)
FIREBASE_ENABLED=false
FIREBASE_SERVICE_ACCOUNT_PATH=/var/www/ibhoom/backend/firebase-service-account.json

# Mapbox (Optional)
MAPBOX_ACCESS_TOKEN=your_mapbox_token_here

# SMTP/Email (Optional)
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@ibhoom.in
```

### Frontend Environment Variables

**Location**: `/var/www/ibhoom/frontend/.env`

```env
VITE_API_URL=https://api.ibhoom.in
```

### Cloudflare Configuration

- **SSL/TLS Mode**: Flexible
- **Always Use HTTPS**: Enabled
- **DNS Records**:
  - A Record: `@` → `88.222.242.64` (Proxied)
  - A Record: `api` → `88.222.242.64` (Proxied)
  - CNAME: `www` → `ibhoom.in` (Proxied)

### Service Accounts

- [ ] Firebase Service Account JSON (if using Firebase)
- [ ] Cloudinary API Credentials (if using Cloudinary)
- [ ] Mapbox Access Token (if using Mapbox)

### Third-Party Services

- [ ] Cloudinary Account
  - Cloud Name: `********`
  - API Key: `********`
  - API Secret: `********`
  
- [ ] Firebase Project
  - Project ID: `********`
  - Service Account Key: `********`
  
- [ ] Mapbox Account
  - Access Token: `********`

---

## 🔒 Security Notes

### Password Generation

**JWT Secret Key:**
```bash
# Generate secure JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# or
openssl rand -hex 32
```

**Database Password:**
- Use strong, random passwords
- Minimum 16 characters
- Include uppercase, lowercase, numbers, special characters

### File Permissions

```bash
# .env files should be readable only by owner
chmod 600 /var/www/ibhoom/backend/.env
chmod 600 /var/www/ibhoom/frontend/.env

# Ownership
chown www-data:www-data /var/www/ibhoom/backend/.env
chown www-data:www-data /var/www/ibhoom/frontend/.env
```

### Backup Credentials

Store backups of credentials in:
- Password manager (1Password, LastPass, Bitwarden)
- Secure vault
- Encrypted file (never commit to Git!)

---

## 📝 Quick Reference

### Where to Find Credentials

| Credential Type | Location |
|----------------|----------|
| Database Password | Backend `.env` file (DATABASE_URL) |
| JWT Secret | Backend `.env` file (JWT_SECRET_KEY) |
| Admin Credentials | Backend `.env` file (ADMIN_EMAIL, ADMIN_PASSWORD) |
| API URL | Frontend `.env` file (VITE_API_URL) |
| Cloudflare Settings | Cloudflare Dashboard |
| Domain Settings | GoDaddy Dashboard |
| VPS Access | Hostinger Dashboard |

### Important URLs

- **Frontend**: https://ibhoom.in
- **Backend API**: https://api.ibhoom.in
- **API Documentation**: https://api.ibhoom.in/docs
- **Health Check**: https://api.ibhoom.in/health

---

## ⚠️ Security Checklist

- [ ] All `.env` files are in `.gitignore`
- [ ] No credentials committed to Git
- [ ] Strong passwords used everywhere
- [ ] File permissions set correctly (600 for .env files)
- [ ] Credentials stored in password manager
- [ ] Regular password rotation scheduled
- [ ] Access logs monitored
- [ ] SSH keys used instead of passwords (recommended)

---

**Last Updated**: November 16, 2025  
**Template Version**: 1.0.0

**Remember**: This is a template. Fill in actual values in a secure location, not in this file!

