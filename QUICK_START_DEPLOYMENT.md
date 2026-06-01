# 🚀 Quick Start: Deploy Full Stack

## Overview

Deploy the complete AI Output Evaluation Tool in 2 steps:
1. **Backend** on Railway (API server)
2. **Frontend** on Vercel (user interface)

**Total time:** ~10 minutes  
**Cost:** ~$5-10/month (Railway has free $5 credit)

---

## Step 1: Deploy Backend (Railway) ⏱️ 5 minutes

### 1.1 Click Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Riya9922/NL-GPT)

### 1.2 Configure Railway

1. **Repository:** `Riya9922/NL-GPT` (auto-selected)
2. **Root Directory:** `backend` ⚠️ **IMPORTANT: Change this!**
3. **Environment Variables:** Click "Add Variable" and add:

```bash
MOCK_MODE=false
GROQ_API_KEY=gsk_your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL_ANALYSIS=llama-3.1-8b-instant
LLM_MODEL_EVAL=llama-3.3-70b-versatile
LLM_MODEL_REGEN=llama-3.3-70b-versatile
CORS_ORIGINS=https://placeholder.vercel.app
MAX_CLAIMS=40
MAX_RESPONSE_CHARS=32000
```

⚠️ **Note:** Replace `https://placeholder.vercel.app` with your actual Vercel URL after Step 2.

4. **Click "Deploy"**
5. **Wait 2-3 minutes**
6. **Copy your backend URL** (e.g., `https://nl-gpt-production.up.railway.app`)

### 1.3 Test Backend

Open new tab and visit: `https://your-backend-url.up.railway.app/health`

Should see:
```json
{
  "status": "ok",
  "mock_mode": false,
  "llm_provider": "groq"
}
```

✅ Backend is ready!

---

## Step 2: Deploy Frontend (Vercel) ⏱️ 5 minutes

### 2.1 Click Deploy Button

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Riya9922/NL-GPT&root-directory=frontend&env=VITE_API_BASE)

### 2.2 Configure Vercel

1. **Repository:** `Riya9922/NL-GPT` (auto-selected)
2. **Root Directory:** `frontend` (auto-set)
3. **Framework Preset:** Vite (auto-detected)
4. **Environment Variables:** Click "Add" and add:

```bash
VITE_API_BASE=https://your-backend-url.up.railway.app
```

⚠️ **Replace with your actual Railway URL from Step 1!**

5. **Click "Deploy"**
6. **Wait 2-3 minutes**
7. **Copy your frontend URL** (e.g., `https://nl-gpt.vercel.app`)

### 2.3 Test Frontend

Visit: `https://your-app.vercel.app`

Should see:
- ✅ Evaluation tool interface
- ✅ Input form
- ✅ Evaluation panel

✅ Frontend is ready!

---

## Step 3: Connect Backend and Frontend 🔗

### 3.1 Update Backend CORS

Go back to Railway dashboard:

1. Click on your project
2. Click **"Variables"** tab
3. Edit `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app,https://your-app.vercel.app
   ```
   Replace `your-app` with your actual Vercel app name.
4. Click **"Add"**
5. Railway will redeploy automatically

### 3.2 Test Full Integration

1. Open your Vercel frontend URL
2. Enter a user query (e.g., "Should we invest in renewable energy?")
3. Enter an AI response (e.g., "Renewable energy is the future...")
4. Click **"Evaluate"**
5. Wait a few seconds
6. See results in evaluation panel!

✅ **Everything is working!** 🎉

---

## 🎯 Share Your App

Once deployed, share your frontend URL with others:

```
https://your-app.vercel.app
```

Anyone can:
- ✅ Access the tool from any browser
- ✅ Submit AI responses for evaluation
- ✅ View detailed analysis
- ✅ Test all features

---

## 📊 What You Get

### Backend (Railway)
- ✅ FastAPI REST endpoints
- ✅ Groq LLM integration
- ✅ Claim verification
- ✅ Source attribution
- ✅ Answer regeneration
- ✅ CORS configured

### Frontend (Vercel)
- ✅ React + Vite interface
- ✅ Evaluation panel
- ✅ Claim highlighting (green/yellow)
- ✅ Source transparency
- ✅ Logic & reasoning check
- ✅ File uploads
- ✅ Auto-deploy on git push

---

## 💰 Cost Breakdown

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| **Railway** | $5 credit/month | $5-10/month |
| **Vercel** | Generous free tier | $0 (free) |
| **Groq API** | Free (rate limited) | $0-5/month |
| **Total** | - | **~$5-15/month** |

---

## 🐛 Troubleshooting

### Issue: "CORS Error"

**Symptom:** Frontend can't connect to backend

**Solution:** Update `CORS_ORIGINS` in Railway to include your Vercel URL:
```bash
CORS_ORIGINS=https://your-app.vercel.app
```

### Issue: "API calls failing"

**Check:**
1. `VITE_API_BASE` in Vercel matches your Railway URL
2. Backend is running (test `/health` endpoint)
3. Browser console for errors

### Issue: "Backend not found"

**Check:**
1. Railway deployment completed
2. Root Directory set to `backend`
3. Environment variables configured

---

## 📚 Additional Documentation

- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Detailed frontend guide
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Detailed backend guide
- [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) - Demo interface setup

---

## ✅ Deployment Checklist

Before sharing:

- [ ] Backend deployed on Railway
- [ ] Backend URL obtained
- [ ] Backend `/health` returns 200 OK
- [ ] Frontend deployed on Vercel
- [ ] `VITE_API_BASE` set correctly
- [ ] `CORS_ORIGINS` updated in Railway
- [ ] Frontend loads without errors
- [ ] Evaluation works end-to-end
- [ ] Shared URL with friends/colleagues

---

## 🎉 Success!

You now have:
- ✅ Public frontend URL on Vercel
- ✅ Backend API on Railway
- ✅ Full evaluation pipeline working
- ✅ Others can access from anywhere
- ✅ Automatic deployments on git push

**Share your URL and start evaluating AI outputs!** 🚀
