# 🌐 Cloudflare + GoDaddy Domain Setup Guide

Complete guide to configure your GoDaddy domain with Cloudflare and connect it to your Hostinger VPS.

---

## 📋 Prerequisites

- ✅ GoDaddy domain (e.g., `yourdomain.com`)
- ✅ Cloudflare account (free tier works)
- ✅ Hostinger VPS with public IP address
- ✅ Nginx installed on VPS

---

## 🔧 Step 1: Add Domain to Cloudflare

### 1.1 Sign Up/Login to Cloudflare

1. Go to [cloudflare.com](https://www.cloudflare.com)
2. Sign up or log in to your account

### 1.2 Add Your Domain

1. Click **"Add a Site"** or **"Add Site"**
2. Enter your domain (e.g., `yourdomain.com`)
3. Click **"Add site"**

### 1.3 Select Plan

- Choose **Free plan** (sufficient for most use cases)
- Click **"Continue"**

### 1.4 Cloudflare Scans Your DNS

- Cloudflare will automatically scan your GoDaddy DNS records
- Review the records found
- Click **"Continue"**

---

## 🔄 Step 2: Update Nameservers in GoDaddy

**This is the most important step!** You need to point your domain to Cloudflare.

### 2.1 Get Cloudflare Nameservers

After adding your domain, Cloudflare will show you **two nameservers**, for example:
```
dante.ns.cloudflare.com
gwen.ns.cloudflare.com
```

**Copy these nameservers!** You'll need them in GoDaddy.

### 2.2 Update Nameservers in GoDaddy

1. **Login to GoDaddy:**
   - Go to [godaddy.com](https://www.godaddy.com)
   - Log in to your account

2. **Navigate to Domains:**
   - Click **"My Products"** or **"Domains"**
   - Find your domain and click **"DNS"** or **"Manage"**

3. **Change Nameservers:**
   - Look for **"Nameservers"** section
   - Click **"Change"** or **"Edit"**
   - Select **"Custom"** or **"I'll use my own nameservers"**
   - Enter the two Cloudflare nameservers:
     ```
     dante.ns.cloudflare.com
     gwen.ns.cloudflare.com
     ```
   - Click **"Save"** or **"Update"**

4. **Wait for Propagation:**
   - DNS changes can take **24-48 hours** to propagate
   - Usually works within **1-2 hours**
   - You can check status in Cloudflare dashboard

---

## 🌍 Step 3: Configure DNS Records in Cloudflare

Once nameservers are updated, configure DNS in Cloudflare:

### 3.1 Access DNS Settings

1. In Cloudflare dashboard, click on your domain
2. Go to **"DNS"** → **"Records"**

### 3.2 Add DNS Records

You need to add records pointing to your VPS IP address.

#### **Record 1: Root Domain (A Record)**

| Type | Name | IPv4 address | Proxy status | TTL |
|------|------|--------------|--------------|-----|
| A | `@` | `YOUR_VPS_IP` | 🟠 Proxied | Auto |

**Example:**
- **Type:** A
- **Name:** `@` (or `yourdomain.com`)
- **IPv4 address:** `123.45.67.89` (your VPS IP)
- **Proxy status:** 🟠 **Proxied** (orange cloud) - **IMPORTANT!**
- **TTL:** Auto

#### **Record 2: WWW Subdomain (A Record)**

| Type | Name | IPv4 address | Proxy status | TTL |
|------|------|--------------|--------------|-----|
| A | `www` | `YOUR_VPS_IP` | 🟠 Proxied | Auto |

**Example:**
- **Type:** A
- **Name:** `www`
- **IPv4 address:** `123.45.67.89` (same VPS IP)
- **Proxy status:** 🟠 **Proxied** (orange cloud)
- **TTL:** Auto

#### **Optional: API Subdomain (if you want separate API domain)**

| Type | Name | IPv4 address | Proxy status | TTL |
|------|------|--------------|--------------|-----|
| A | `api` | `YOUR_VPS_IP` | 🟠 Proxied | Auto |

**Example:**
- **Type:** A
- **Name:** `api`
- **IPv4 address:** `123.45.67.89` (same VPS IP)
- **Proxy status:** 🟠 **Proxied** (orange cloud)
- **TTL:** Auto

### 3.3 Important: Proxy Status

- **🟠 Orange Cloud (Proxied):** 
  - ✅ Traffic goes through Cloudflare (DDoS protection, CDN, SSL)
  - ✅ Hides your server IP
  - ✅ **Recommended for production**
  
- **⚪ Grey Cloud (DNS Only):**
  - ⚠️ Direct connection to your server
  - ⚠️ No Cloudflare protection
  - ⚠️ Use only for testing or if you have issues

**For production, always use 🟠 Proxied (orange cloud)!**

---

## 🔒 Step 4: Configure SSL/TLS in Cloudflare

### 4.1 SSL/TLS Settings

1. In Cloudflare dashboard, go to **"SSL/TLS"**
2. Select **"Full"** or **"Full (strict)"** mode:
   - **Full:** Cloudflare ↔ Your server (can use self-signed cert)
   - **Full (strict):** Cloudflare ↔ Your server (requires valid cert)
   
   **For now, use "Full"** - we'll set up Let's Encrypt later.

### 4.2 Always Use HTTPS

1. Go to **"SSL/TLS"** → **"Edge Certificates"**
2. Enable **"Always Use HTTPS"** (redirects HTTP to HTTPS)
3. Enable **"Automatic HTTPS Rewrites"**

### 4.3 Minimum TLS Version

- Set to **TLS 1.2** or higher (recommended: **TLS 1.3**)

---

## ⚙️ Step 5: Update Nginx Configuration

Now update your Nginx config with your domain name.

### 5.1 Edit Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/ibhoom
```

### 5.2 Update Server Name

Find this line:
```nginx
server_name _;  # Replace with your domain name
```

Replace with your actual domain:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

**Example:**
```nginx
server_name ibhoom.com www.ibhoom.com;
```

### 5.3 Complete Nginx Configuration

Your config should look like this:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;  # ← Your domain here
    
    # Logging
    access_log /var/log/nginx/ibhoom_access.log;
    error_log /var/log/nginx/ibhoom_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # Frontend - React app (static files)
    location / {
        root /var/www/ibhoom/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Uploads and static files
    location /uploads/ {
        alias /var/www/ibhoom/backend/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend;
        access_log off;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 5.4 Test and Reload Nginx

```bash
# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

---

## 🔍 Step 6: Verify DNS Propagation

### 6.1 Check DNS Propagation

Use these tools to check if DNS has propagated:

- **DNS Checker:** [dnschecker.org](https://dnschecker.org)
- **What's My DNS:** [whatsmydns.net](https://whatsmydns.net)

Enter your domain and check if it resolves to your VPS IP.

### 6.2 Test from Command Line

```bash
# Check A record
dig yourdomain.com +short

# Should return your VPS IP
# Example: 123.45.67.89

# Check www subdomain
dig www.yourdomain.com +short
```

### 6.3 Test Website Access

Once DNS propagates (usually 1-2 hours):

```bash
# Test HTTP
curl -I http://yourdomain.com

# Should return HTTP 200 or 301/302
```

---

## 🔒 Step 7: Setup SSL Certificate (Let's Encrypt)

Even though Cloudflare provides SSL, it's good to have SSL on your server too.

### 7.1 Install Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2 Obtain SSL Certificate

**Important:** For Cloudflare, you have two options:

#### **Option A: Let Cloudflare Handle SSL (Easier)**

- Cloudflare automatically provides SSL
- No need to install Let's Encrypt on server
- **Recommended for beginners**

#### **Option B: Full SSL with Let's Encrypt (Advanced)**

If you want SSL on your server too:

```bash
# Temporarily disable Cloudflare proxy (grey cloud) for SSL verification
# Then run:
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# After certificate is obtained, re-enable Cloudflare proxy (orange cloud)
```

**Note:** With Cloudflare proxy enabled, Let's Encrypt verification might fail. You can use Cloudflare's SSL instead.

---

## ⚙️ Step 8: Cloudflare Performance Settings

### 8.1 Speed Optimization

1. Go to **"Speed"** → **"Optimization"**
2. Enable:
   - ✅ **Auto Minify** (CSS, JavaScript, HTML)
   - ✅ **Brotli** compression
   - ✅ **Rocket Loader** (optional)

### 8.2 Caching

1. Go to **"Caching"** → **"Configuration"**
2. Set **Caching Level:** Standard
3. Set **Browser Cache TTL:** 4 hours (or longer)

### 8.3 Page Rules (Optional)

Create rules for better caching:

1. Go to **"Rules"** → **"Page Rules"**
2. Create rule: `yourdomain.com/api/*`
   - **Setting:** Cache Level: Bypass
   - (API responses shouldn't be cached)

---

## 🔧 Step 9: Update Backend CORS Settings

Update your backend to allow your domain:

### 9.1 Edit Backend .env

```bash
cd /var/www/ibhoom/backend
nano .env
```

### 9.2 Update CORS Origins

```env
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,http://localhost:3000
```

### 9.3 Restart Backend

```bash
sudo systemctl restart ibhoom-backend
```

---

## 🔧 Step 10: Update Frontend API URL

### 10.1 Edit Frontend .env

```bash
cd /var/www/ibhoom/frontend
nano .env
```

### 10.2 Update API URL

```env
VITE_API_URL=https://yourdomain.com
```

### 10.3 Rebuild Frontend

```bash
npm run build
```

### 10.4 Reload Nginx

```bash
sudo systemctl reload nginx
```

---

## ✅ Verification Checklist

- [ ] Domain added to Cloudflare
- [ ] Nameservers updated in GoDaddy
- [ ] DNS records added in Cloudflare (A records)
- [ ] DNS propagated (check with dnschecker.org)
- [ ] Nginx config updated with domain name
- [ ] Nginx test passed (`nginx -t`)
- [ ] Nginx reloaded
- [ ] Website accessible via domain
- [ ] SSL working (HTTPS redirects)
- [ ] Backend CORS updated
- [ ] Frontend API URL updated
- [ ] Frontend rebuilt

---

## 🐛 Troubleshooting

### Problem: "Domain not resolving"

**Solutions:**
1. Check if nameservers are updated in GoDaddy
2. Wait 24-48 hours for DNS propagation
3. Clear DNS cache: `sudo systemd-resolve --flush-cache`
4. Check DNS records in Cloudflare dashboard

### Problem: "502 Bad Gateway"

**Solutions:**
1. Check if backend is running: `sudo systemctl status ibhoom-backend`
2. Check backend logs: `sudo journalctl -u ibhoom-backend -f`
3. Test backend directly: `curl http://localhost:8000/health`
4. Check Nginx error logs: `sudo tail -f /var/log/nginx/ibhoom_error.log`

### Problem: "SSL Certificate Error"

**Solutions:**
1. If using Cloudflare, SSL is automatic (orange cloud)
2. If using Let's Encrypt, temporarily disable Cloudflare proxy
3. Check SSL mode in Cloudflare: Should be "Full" or "Full (strict)"

### Problem: "CORS Error"

**Solutions:**
1. Update `BACKEND_CORS_ORIGINS` in backend `.env`
2. Include both `https://yourdomain.com` and `https://www.yourdomain.com`
3. Restart backend: `sudo systemctl restart ibhoom-backend`

### Problem: "API calls failing"

**Solutions:**
1. Check frontend `.env` has correct `VITE_API_URL`
2. Rebuild frontend: `npm run build`
3. Check browser console for errors
4. Verify backend is accessible: `curl https://yourdomain.com/api/health`

---

## 📊 Cloudflare Dashboard Overview

### Key Sections:

1. **Overview:** Domain status, analytics
2. **DNS:** Manage DNS records
3. **SSL/TLS:** SSL settings and certificates
4. **Speed:** Performance optimizations
5. **Caching:** Cache configuration
6. **Security:** Firewall, DDoS protection
7. **Analytics:** Traffic and performance metrics

---

## 🎯 Quick Reference Commands

```bash
# Check DNS resolution
dig yourdomain.com +short

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check backend status
sudo systemctl status ibhoom-backend

# View Nginx logs
sudo tail -f /var/log/nginx/ibhoom_error.log

# Test website
curl -I https://yourdomain.com
```

---

## 🎉 Success!

Once everything is configured:

- ✅ Your domain should be accessible at `https://yourdomain.com`
- ✅ Frontend should load correctly
- ✅ API calls should work
- ✅ SSL should be active (green padlock)
- ✅ Cloudflare protection is active

**Your ibhoom application is now live with a custom domain!** 🚀

---

## 📞 Need Help?

- **Cloudflare Support:** [support.cloudflare.com](https://support.cloudflare.com)
- **GoDaddy Support:** [help.godaddy.com](https://help.godaddy.com)
- **Check DNS:** [dnschecker.org](https://dnschecker.org)
- **Test SSL:** [ssllabs.com/ssltest](https://www.ssllabs.com/ssltest)

