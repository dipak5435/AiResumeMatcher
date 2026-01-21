# Railway Deployment Guide

## ✅ Pre-Deployment Checklist

All files are ready for Railway deployment:

### Files Created:
- ✅ `Procfile` - Tells Railway how to run your app
- ✅ `runtime.txt` - Specifies Python version (3.11.0)
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `.env.railway` - Template for Railway environment variables

---

## 🚀 Deployment Steps

### Step 1: Get Google API Key (2 minutes)

1. Go to **https://aistudio.google.com/app/apikey**
2. Click **"Get API Key"** → **"Create API key in new project"**
3. Copy the generated key
4. Save it securely (you'll need it in Step 5)

### Step 2: Push Code to GitHub (5 minutes)

```bash
# Navigate to project
cd d:\AiResumeTask

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "AI Resume Matcher - Production ready"

# Create GitHub repo at https://github.com/new
# Then connect local repo:
git remote add origin https://github.com/YOUR_USERNAME/AiResumeTask.git
git branch -M main
git push -u origin main
```

### Step 3: Create Railway Account (2 minutes)

1. Go to **https://railway.app**
2. Click **"Start Project"**
3. Sign up with **GitHub** (easiest)
4. Authorize Railway to access your repos

### Step 4: Deploy on Railway (3 minutes)

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Search and select **"AiResumeTask"**
4. Click **"Deploy Now"**

Railway automatically detects Flask and creates the deployment ✅

### Step 5: Add Environment Variables (2 minutes)

1. Go to your Railway project dashboard
2. Click the **project name** → **Variables**
3. Click **"Add Variable"**
4. Add these:

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | `your_actual_api_key_from_step_1` |
| `FLASK_DEBUG` | `False` |
| `DATABASE_URL` | `sqlite:///resume_matcher.db` |

5. Click **"Save"**

### Step 6: Monitor Deployment (2-3 minutes)

1. Click **"Deployments"** tab
2. Watch the build logs
3. When status shows **"Running"** = Success! ✅

### Step 7: Access Your Live App (1 minute)

1. Click **"Settings"** tab
2. Look for **"Domains"** section
3. You'll see: `https://airesumetask-production.up.railway.app` (or similar)
4. Click the URL to open your app

---

## ✨ Your App is Live!

You can now:
- ✅ Upload resumes
- ✅ Paste job descriptions
- ✅ Get AI-powered match scores
- ✅ View recommendations
- ✅ Access from anywhere

Share the URL with others! 🎉

---

## 📊 What Gets Deployed

Railway automatically:
1. **Detects Python** from `requirements.txt`
2. **Installs dependencies** including gunicorn
3. **Runs Procfile** command to start web server
4. **Uses environment variables** for API keys
5. **Stores SQLite database** in Railway filesystem
6. **Assigns public URL** to your app

---

## 🔧 Troubleshooting

### Deployment Failed?

Check logs in Railway dashboard:
```
Deployments → Click failed deployment → View Logs
```

**Common issues:**

| Error | Solution |
|-------|----------|
| `gunicorn not found` | Check `requirements.txt` has gunicorn |
| `GOOGLE_API_KEY not set` | Add GOOGLE_API_KEY to Railway Variables |
| `ModuleNotFoundError` | Ensure all imports are in `requirements.txt` |
| `Port already in use` | Railway handles PORT automatically |

### Redeploy After Code Changes

```bash
# Make changes locally
# Commit and push
git add .
git commit -m "Update matcher logic"
git push origin main

# Railway auto-detects push and redeploys automatically!
```

---

## 💰 Free Tier Details

**Railway Free Plan:**
- Monthly credit: $5 USD
- Running time: ~500 hours/month (16+ hrs/day)
- Database storage: Unlimited
- **Status**: ✅ Perfect for MVP & testing

**Cost breakdown:**
- Running continuously: ~$0.50/hour
- 8 hours/day = ~$120/month (exceeds free tier, but starts with $5 credit)
- **Recommendation**: Deploy, test, keep running if under $5/month

---

## 📈 After Deployment

### Monitor Your App
- Railway dashboard shows active deployments
- View logs for errors
- Check resource usage

### Make Updates
- Edit code locally
- Push to GitHub
- Railway auto-redeploys

### Scale Up
- Add PostgreSQL database (Railway marketplace)
- Upgrade to paid plan for more resources
- Add custom domain

---

## ✅ Your Project is Production Ready!

Everything needed for Railway deployment is configured:
- ✅ `Procfile` - Run configuration
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - All dependencies
- ✅ `.env.example` - Environment template
- ✅ Code - Clean & modular

**Next Step**: Follow the 7 deployment steps above! 🚀
