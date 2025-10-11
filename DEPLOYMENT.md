# 🚀 Deployment Guide - ibhoom Backend on Render

This guide will help you deploy the ibhoom backend to Render.com.

## 📋 Prerequisites

- GitHub repository with your ibhoom code
- Render.com account (free tier available)
- Your frontend URL (for CORS configuration)

## 🔧 Render Configuration

### **1. Create New Web Service**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### **2. Configure Service Settings**

| Setting | Value |
|---------|-------|
| **Root Directory** | `backend` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### **3. Environment Variables**

Add these environment variables in Render dashboard:

| Key | Value | Description |
|-----|-------|-------------|
| `JWT_SECRET_KEY` | `your-super-secret-production-key` | **Change this!** Use a strong random string |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |
| `BACKEND_CORS_ORIGINS` | `https://your-frontend.onrender.com,http://localhost:5173` | Your frontend URLs |
| `DEBUG` | `false` | Disable debug mode for production |
| `DATABASE_URL` | `sqlite:///./marketplace.db` | Database URL (SQLite for free tier) |

### **4. Advanced Settings**

- **Auto-Deploy**: Enable (deploys on git push)
- **Health Check Path**: `/health`
- **Plan**: Free (or upgrade as needed)

## 🔄 Deployment Process

### **Step 1: Prepare Your Repository**

Make sure your `backend/` directory contains:
- ✅ `requirements.txt`
- ✅ `init_db.py` (database initialization)
- ✅ `Procfile` (startup command)
- ✅ `runtime.txt` (Python version)

### **Step 2: Deploy**

1. **Push to GitHub**: Commit and push your changes
2. **Render Auto-Deploy**: Render will automatically detect changes and redeploy
3. **Monitor Logs**: Check the Render dashboard for deployment logs

### **Step 3: Verify Deployment**

1. **Health Check**: Visit `https://your-app.onrender.com/health`
2. **API Docs**: Visit `https://your-app.onrender.com/docs`
3. **Test Endpoints**: Use the interactive API documentation

## 🔧 Configuration Files

### **render.yaml** (Optional - for advanced configuration)
```yaml
services:
  - type: web
    name: ibhoom-backend
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      python init_db.py
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: BACKEND_CORS_ORIGINS
        value: https://your-frontend.onrender.com
```

### **Procfile**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **runtime.txt**
```
python-3.11.0
```

## 🔒 Security Considerations

### **Production Checklist**
- ✅ Change `JWT_SECRET_KEY` to a strong random string
- ✅ Set `DEBUG=false`
- ✅ Configure proper CORS origins
- ✅ Use HTTPS in production
- ✅ Consider upgrading to paid plan for better performance

### **Environment Variables Security**
```bash
# Generate a secure JWT secret
openssl rand -hex 32
```

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Build Failures**
```bash
# Check if all dependencies are in requirements.txt
pip freeze > requirements.txt
```

#### **2. Database Issues**
```bash
# The database is created automatically on first startup
# Check logs for database initialization messages
```

#### **3. CORS Errors**
```bash
# Make sure your frontend URL is in BACKEND_CORS_ORIGINS
# Format: https://your-frontend.onrender.com,http://localhost:5173
```

#### **4. Port Issues**
```bash
# Render automatically sets the PORT environment variable
# Make sure your start command uses $PORT
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Debugging Steps**

1. **Check Render Logs**: Go to your service → Logs tab
2. **Test Health Endpoint**: `GET /health`
3. **Check Environment Variables**: Verify all required vars are set
4. **Database Connection**: Check if database is being created

## 📊 Monitoring

### **Render Dashboard**
- **Metrics**: CPU, Memory, Response Time
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### **Health Checks**
- **Endpoint**: `/health`
- **Expected Response**: `{"status": "healthy"}`
- **Frequency**: Render checks this automatically

## 🔄 Updates and Maintenance

### **Updating Your App**
1. **Make Changes**: Update your code locally
2. **Test Locally**: Ensure everything works
3. **Commit & Push**: Push to GitHub
4. **Auto-Deploy**: Render automatically deploys the changes

### **Database Backups**
- **SQLite**: Database file is stored on Render's filesystem
- **Backup**: Consider upgrading to PostgreSQL for better data persistence
- **Export**: Use Render's shell access to export data if needed

## 💰 Cost Optimization

### **Free Tier Limits**
- **Sleep Mode**: App sleeps after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes ~30 seconds
- **Bandwidth**: 100GB/month included
- **Build Time**: 500 minutes/month

### **Upgrade Options**
- **Starter Plan**: $7/month - No sleep mode, better performance
- **Standard Plan**: $25/month - More resources, better reliability

## 🎯 Next Steps

After successful deployment:

1. **Update Frontend**: Point your frontend to the new backend URL
2. **Test Integration**: Verify all API calls work
3. **Monitor Performance**: Watch metrics and logs
4. **Set Up Monitoring**: Consider adding error tracking
5. **Backup Strategy**: Plan for data persistence

## 📞 Support

If you encounter issues:

1. **Check Render Logs**: Most issues are visible in the logs
2. **Render Support**: Use Render's support system
3. **GitHub Issues**: Create an issue in your repository
4. **Community**: Check FastAPI and Render documentation

---

**🎉 Congratulations! Your ibhoom backend is now live on Render!**
