# 🔧 Fix: "Environment variable does not exist" Error

## Problem

When deploying to Vercel, you see:
```
Error: Environment variable VITE_API_BASE does not exist
```

## ✅ Solution Applied

I've fixed the `vercel.json` file to properly handle environment variables.

### What Changed

**Old vercel.json (Incorrect):**
```json
{
  "build": {
    "env": {
      "VITE_API_BASE": "@vite_api_base"  // ❌ Wrong syntax
    }
  }
}
```

**New vercel.json (Correct):**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Why this works:** Vite automatically detects `VITE_*` environment variables from the Vercel dashboard during build time. No explicit mapping needed!

---

## 🚀 Deploy Again

### Step 1: Go Back to Vercel

1. Open your Vercel project
2. Click **"Settings"** → **"Environment Variables"**
3. Verify `VITE_API_BASE` is configured:
   ```
   VITE_API_BASE = https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app
   ```
4. **Select all environments:**
   - ✅ Production
   - ✅ Preview
   - ✅ Development

### Step 2: Redeploy

1. Click **"Deployments"** tab
2. Find the latest deployment
3. Click the **three dots (⋮)** → **"Redeploy"**
4. Wait 2-3 minutes

### Step 3: Test

1. Open your Vercel URL
2. Should load without errors
3. Try an evaluation
4. Should work!

---

## 🔍 Verify Environment Variable

### In Vercel Dashboard

1. Go to your project
2. Click **"Settings"** → **"Environment Variables"**
3. You should see:
   ```
   VITE_API_BASE
   Value: https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app
   Environments: ☑️ Production  ☑️ Preview  ☑️ Development
   ```

### In Build Logs

After redeployment, check the build logs:
1. Click on the deployment
2. Click **"View Build Logs"**
3. Look for:
   ```
   VITE_API_BASE: https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app
   ```

---

## 🐛 Still Not Working?

### Check 1: Variable Name Spelling

Make sure the variable name is exactly:
```
VITE_API_BASE
```
(All uppercase, with underscore)

### Check 2: Variable Value

Make sure the value is:
```
https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app
```
(No trailing slash)

### Check 3: Environments Selected

Make sure you've selected:
- ☑️ Production
- ☑️ Preview
- ☑️ Development

### Check 4: Git Commit Pulled

Make sure Vercel has pulled the latest commit (`24db414`):
1. Go to **"Deployments"** tab
2. Check the latest deployment
3. Should show commit: `24db414`
4. If not, click **"Redeploy"**

---

## ✅ Success Indicators

After successful deployment, you'll see:

1. ✅ **Build succeeds** (no errors in logs)
2. ✅ **Frontend loads** at your Vercel URL
3. ✅ **No console errors** about missing variables
4. ✅ **API calls work** (check Network tab)

---

## 📊 What to Do Next

After frontend deploys successfully:

### Update Streamlit CORS

1. Go to Streamlit Cloud: https://share.streamlit.io
2. Click your app: `nl-gpt`
3. Click **three dots (⋮)** → **"Settings"** → **"Secrets"**
4. Add this line (replace `your-app-name` with your Vercel URL):

```toml
CORS_ORIGINS = "https://your-app-name.vercel.app,https://your-app-name-git-main.vercel.app"
```

5. Click **"Save"**
6. Wait for Streamlit to redeploy (1-2 minutes)

### Test Integration

1. Open your Vercel frontend
2. Enter a user query
3. Enter an AI response
4. Click "Evaluate"
5. See results!

---

## 🎯 Quick Summary

**Problem:** Vercel couldn't find `VITE_API_BASE` variable  
**Cause:** Incorrect syntax in `vercel.json`  
**Fix:** Simplified `vercel.json` - Vite auto-detects VITE_* variables  
**Status:** ✅ Fixed and pushed to GitHub

**Next:** Redeploy on Vercel and it should work!

---

**Your frontend will be live in 5 minutes!** 🚀
