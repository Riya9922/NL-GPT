# 🚀 Frontend Deployment Guide (Vercel)

## Quick Deploy

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Riya9922/NL-GPT&root-directory=frontend&env=VITE_API_BASE)

**What this does:**
- Imports your GitHub repository
- Sets root directory to `frontend`
- Prompts for `VITE_API_BASE` environment variable

---

## 📋 Manual Deployment Steps

### Step 1: Deploy Backend First (Required)

Before deploying the frontend, you need a backend API URL.

**Option A: Deploy on Railway (Recommended)**
1. Go to [railway.app](https://railway.app)
2. Deploy from `Riya9922/NL-GPT`
3. Set **Root Directory** to `backend`
4. Add environment variables
5. Get your backend URL (e.g., `https://nl-gpt-backend.up.railway.app`)

**Option B: Deploy on Render**
1. Go to [render.com](https://render.com)
2. Similar setup as Railway
3. Get your backend URL

**Option C: Use Streamlit Cloud (Demo Only)**
- Streamlit Cloud is for demo only
- Does NOT provide REST API endpoints
- Frontend won't work with Streamlit backend

See [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) for backend deployment.

---

### Step 2: Deploy Frontend to Vercel

1. **Go to** [vercel.com/new](https://vercel.com/new)

2. **Import Repository**
   - Click "Import Git Repository"
   - Select `Riya9922/NL-GPT`
   - Click "Import"

3. **Configure Project**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

4. **Add Environment Variables**
   Click **"Environment Variables"** and add:
   ```
   Name: VITE_API_BASE
   Value: https://your-backend-url.railway.app
   Environment: Production, Preview, Development
   ```
   Replace `your-backend-url.railway.app` with your actual backend URL from Step 1.

5. **Deploy**
   - Click **"Deploy"**
   - Wait 2-3 minutes
   - You'll get a URL like: `https://nl-gpt.vercel.app`

---

## 🧪 Test the Deployment

### 1. Open Frontend URL
Visit: `https://your-app.vercel.app`

### 2. Check Backend Connection
Open browser console (F12) and check for:
- ✅ No CORS errors
- ✅ API calls succeed
- ✅ Data loads correctly

### 3. Test Evaluation
1. Enter a user query
2. Enter an AI response
3. Enable claim verification (optional)
4. Click "Evaluate"
5. Check results in evaluation panel

---

## 🔧 Configuration Details

### Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_BASE` | ✅ | `https://nl-gpt-backend.up.railway.app` |

**How to add in Vercel:**
1. Go to your project in Vercel dashboard
2. Click **Settings** → **Environment Variables**
3. Add variable for Production, Preview, and Development
4. Click **Save**
5. Redeploy the project

### CORS Configuration (Backend)

Your backend (Railway/Render) must allow your Vercel frontend:

```bash
# In Railway/Render environment variables:
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app,https://your-app.vercel.app
```

---

## 📁 File Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # Uses VITE_API_BASE
│   ├── components/
│   ├── App.tsx
│   └── main.tsx
├── .env.example               # Template for environment variables
├── .env.vercel                # Example Vercel config
├── vercel.json                # Vercel configuration
├── package.json
└── vite.config.ts
```

---

## 🐛 Troubleshooting

### Issue 1: "API calls failing"

**Symptom:** Clicking "Evaluate" shows error

**Solutions:**
1. Check `VITE_API_BASE` is set correctly in Vercel
2. Verify backend is running: `curl https://your-backend-url.railway.app/health`
3. Check browser console for CORS errors
4. Update backend `CORS_ORIGINS` to include your Vercel URL

### Issue 2: "CORS Error"

**Symptom:** Browser console shows:
```
Access to fetch at 'https://backend.railway.app' from origin 'https://frontend.vercel.app' 
has been blocked by CORS policy
```

**Solution:** Add your Vercel URL to backend's `CORS_ORIGINS`:
```bash
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

### Issue 3: "Build Failed"

**Symptom:** Vercel deployment shows build errors

**Solutions:**
1. Check build logs in Vercel dashboard
2. Ensure `package.json` has correct dependencies
3. Test build locally: `cd frontend && npm run build`
4. Fix any TypeScript errors

### Issue 4: "404 on page refresh"

**Symptom:** Refreshing page shows 404 error

**Solution:** The `vercel.json` already includes SPA routing configuration:
```json
{
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

---

## 🔍 Verify Deployment

### Check Backend Health
```bash
curl https://your-backend-url.railway.app/health
```

Expected:
```json
{
  "status": "ok",
  "mock_mode": false,
  "llm_provider": "groq"
}
```

### Check Frontend Connection
1. Open frontend in browser
2. Open DevTools (F12) → Network tab
3. Refresh page
4. Look for `/health` request
5. Should show status 200 OK

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│  Users                                  │
│  - Access frontend URL                  │
│  - Submit evaluation requests           │
└────────────┬────────────────────────────┘
             │
             │ HTTPS
             │
┌────────────▼────────────────────────────┐
│  Frontend (Vercel)                      │
│  - React + Vite + Tailwind              │
│  - Static site                          │
│  - Calls backend API                    │
│  - URL: https://your-app.vercel.app     │
└────────────┬────────────────────────────┘
             │
             │ HTTPS (VITE_API_BASE)
             │
┌────────────▼────────────────────────────┐
│  Backend (Railway/Render)               │
│  - FastAPI + Uvicorn                    │
│  - REST API endpoints                   │
│  - Calls Groq LLM API                   │
│  - URL: https://backend.up.railway.app  │
└─────────────────────────────────────────┘
```

---

## 💰 Cost Estimate

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **Vercel** | Generous free tier | $20/month (Pro) |
| **Railway** | $5 credit/month | $5-20/month |
| **Groq API** | Free (rate limited) | Pay per usage |

**Total for small projects:** ~$5-10/month

---

## ✅ Deployment Checklist

Before going live:

- [ ] Backend deployed on Railway/Render
- [ ] Backend URL obtained
- [ ] Backend `CORS_ORIGINS` includes Vercel URL
- [ ] Frontend deployed on Vercel
- [ ] `VITE_API_BASE` set to backend URL
- [ ] Frontend loads without errors
- [ ] Evaluation works end-to-end
- [ ] Tested in multiple browsers
- [ ] Shared URL with others for testing

---

## 🎯 After Deployment

### Share Your App

Once deployed, share your frontend URL:
```
https://your-app.vercel.app
```

Others can:
- ✅ Access the evaluation tool
- ✅ Submit AI responses for evaluation
- ✅ View results in the evaluation panel
- ✅ Test all features

### Monitor Usage

Check Vercel dashboard for:
- Page views
- API calls
- Error rates
- Performance metrics

---

## 🔄 Updating Deployment

When you make changes:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

2. **Vercel auto-deploys**
   - Automatic deployment on push to main
   - Preview deployments for pull requests

3. **Test preview URL**
   - Vercel creates preview for each PR
   - Test before merging to main

---

## 📞 Support

- **Vercel Docs:** [vercel.com/docs](https://vercel.com/docs)
- **Vite Docs:** [vitejs.dev](https://vitejs.dev)
- **Issues:** [github.com/Riya9922/NL-GPT/issues](https://github.com/Riya9922/NL-GPT/issues)

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Public frontend URL on Vercel
- ✅ Backend API on Railway/Render
- ✅ Full evaluation pipeline working
- ✅ Others can access and test
- ✅ Automatic deployments on git push

**Ready to share with the world!** 🚀
