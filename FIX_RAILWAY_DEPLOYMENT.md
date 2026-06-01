# 🔧 Fix Railway Deployment Failure

## Problem

Railway deployment failed with build error.

**Root Cause:** Likely one of these issues:
1. Missing or incorrect environment variables
2. Wrong root directory configuration
3. CORS_ORIGINS still set to localhost (visible in screenshot)

---

## ✅ Step-by-Step Fix

### Step 1: Verify Railway Configuration

Go to your Railway project dashboard and check:

#### 1.1 Root Directory

**Settings** → **Source** → **Root Directory** should be:
```
backend
```

⚠️ **This is critical!** If it's empty or set to root `/`, Railway will fail.

#### 1.2 Environment Variables

**Settings** → **Variables** should have:

```bash
MOCK_MODE=false
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
LLM_PROVIDER=groq
LLM_MODEL_ANALYSIS=llama-3.1-8b-instant
LLM_MODEL_EVAL=llama-3.3-70b-versatile
LLM_MODEL_REGEN=llama-3.3-70b-versatile
CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-git-main.vercel.app
MAX_CLAIMS=40
MAX_RESPONSE_CHARS=32000
ENABLE_WEB_SEARCH=false
```

⚠️ **Update CORS_ORIGINS** to include your Vercel URL (not localhost!)

---

### Step 2: Check Build Logs

1. Go to Railway dashboard
2. Click on your project
3. Click **"Deployments"** tab
4. Find the failed deployment
5. Click **"View Logs"**
6. Look for error messages

**Common errors:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Root Directory not set to `backend` |
| `GROQ_API_KEY not set` | Add GROQ_API_KEY to Railway variables |
| `Port 8001 not available` | Don't hardcode port, use `$PORT` env var |
| `Build failed` | Check requirements.txt and Python version |

---

### Step 3: Update CORS_ORIGINS

From your screenshot, `CORS_ORIGINS` is set to:
```
http://localhost:5173,http://127.0.0.1:5173
```

**This is wrong for production!** Update it to:

```bash
CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-vercel-app-git-main.vercel.app,https://your-vercel-app.vercel.app
```

**Replace `your-vercel-app`** with your actual Vercel URL from the browser address bar.

---

### Step 4: Verify Procfile

Make sure `backend/Procfile` exists and contains:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This tells Railway how to start the server.

---

### Step 5: Redeploy

After fixing the issues:

1. **Update environment variables** in Railway
2. **Click "Redeploy"** or push a new commit
3. **Wait 2-3 minutes**
4. **Check build logs** for success

---

## 🔍 Verification Checklist

After successful deployment:

- [ ] Railway shows **"Success"** status
- [ ] Railway URL is accessible (e.g., `https://nl-gpt.up.railway.app`)
- [ ] `https://your-railway-url.up.railway.app/health` returns:
  ```json
  {
    "status": "ok",
    "mock_mode": false,
    "llm_provider": "groq"
  }
  ```
- [ ] No errors in Railway logs
- [ ] CORS_ORIGINS includes your Vercel URL

---

## 📊 Common Railway Issues & Solutions

### Issue 1: "No start command found"

**Solution:** Add Procfile to `backend/` directory:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue 2: "Python not found"

**Solution:** Railway should auto-detect Python from `requirements.txt`. If not, add to Railway variables:
```
RAILWAY_STATIC_PYTHON_VERSION=3.11
```

### Issue 3: "Port already in use"

**Solution:** Never hardcode port. Always use `$PORT`:
```bash
# ❌ Wrong
uvicorn app.main:app --port 8001

# ✅ Correct
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Issue 4: "Module not found"

**Solution:** Root Directory must be set to `backend` in Railway settings.

---

## 🎯 After Railway Succeeds

### Update Frontend (Vercel)

1. Go to Vercel project
2. **Settings** → **Environment Variables**
3. Update `VITE_API_BASE`:
   ```
   VITE_API_BASE=https://your-railway-url.up.railway.app
   ```
4. **Deployments** → **Redeploy**
5. Wait 2-3 minutes

### Test Integration

1. Open Vercel frontend
2. Enter user query
3. Enter AI response
4. Click "Evaluate"
5. Should work! ✅

---

## 📞 Still Failing?

### Collect This Info:

1. **Railway build logs:**
   - Copy the full error message
   - Note which step failed (build, start, etc.)

2. **Configuration:**
   - Root Directory setting
   - All environment variables
   - Procfile contents

3. **GitHub commit:**
   - Latest commit hash
   - Any recent changes to backend/

### Get Help:

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Create issue: https://github.com/Riya9922/NL-GPT/issues

---

## ✅ Quick Fix Summary

**Most likely cause:** CORS_ORIGINS still set to localhost

**Quick fix:**
1. Update `CORS_ORIGINS` in Railway to use Vercel URL
2. Verify Root Directory = `backend`
3. Verify `GROQ_API_KEY` is set
4. Redeploy

---

**Railway deployment should work after these fixes!** 🚀
