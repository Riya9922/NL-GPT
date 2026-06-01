# 🚀 Vercel Frontend Deployment (with Streamlit Backend)

## Your Backend URL

**Backend (Streamlit Cloud):** `https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app`

---

## Quick Deploy Frontend to Vercel

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Riya9922/NL-GPT&root-directory=frontend&env=VITE_API_BASE)

### Manual Steps

1. **Go to** [vercel.com/new](https://vercel.com/new)

2. **Import Repository**
   - Click "Import Git Repository"
   - Select `Riya9922/NL-GPT`
   - Click "Import"

3. **Configure Project**
   - **Framework Preset:** Vite (auto-detected)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. **Add Environment Variable**
   Click **"Environment Variables"** and add:
   ```
   Name: VITE_API_BASE
   Value: https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app
   Environment: Production, Preview, Development
   ```

5. **Deploy**
   - Click **"Deploy"**
   - Wait 2-3 minutes
   - Copy your frontend URL (e.g., `https://nl-gpt.vercel.app`)

---

## ⚠️ Important: Update Streamlit CORS

Your Streamlit backend must allow requests from your Vercel frontend.

### Update Streamlit Secrets

1. Go to your Streamlit Cloud dashboard
2. Click on your app: `nl-gpt-azzfyfpjss6xw5tsgo6lc`
3. Click **"Settings"** → **"Secrets"**
4. Add or update `CORS_ORIGINS`:

```toml
CORS_ORIGINS = "https://your-app.vercel.app,https://your-app-git-main.vercel.app,https://your-app.vercel.app"
```

**Replace `your-app` with your actual Vercel app name!**

5. Click **"Save"**
6. Streamlit will automatically redeploy

---

## Test the Integration

### 1. Open Frontend

Visit: `https://your-app.vercel.app`

### 2. Test Evaluation

1. Enter user query: "Should we invest in renewable energy?"
2. Enter AI response: "Renewable energy is the future. Solar panels are very efficient."
3. Click **"Evaluate"**
4. Wait 5-10 seconds
5. See results in evaluation panel

### 3. Check Browser Console

Open DevTools (F12) → Console tab:
- ✅ No CORS errors
- ✅ API calls succeed
- ✅ Data loads correctly

---

## Troubleshooting

### Issue: "CORS Error"

**Symptom:**
```
Access to fetch at 'https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app' 
from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**Solution:**
Update `CORS_ORIGINS` in Streamlit secrets to include your Vercel URL (see above).

### Issue: "Cannot reach API"

**Check:**
1. Streamlit backend is running: Visit `https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app`
2. `VITE_API_BASE` in Vercel matches the Streamlit URL
3. Streamlit secrets include `CORS_ORIGINS`

### Issue: "Build Failed"

**Check:**
1. Vercel build logs for errors
2. Test locally: `cd frontend && npm run build`
3. Ensure `package.json` dependencies are correct

---

## Your Deployment URLs

| Service | URL |
|---------|-----|
| **Backend** | https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app |
| **Frontend** | https://your-app.vercel.app (after deployment) |
| **GitHub** | https://github.com/Riya9922/NL-GPT |

---

## Share Your App

Once deployed, share your frontend URL:

```
https://your-app.vercel.app
```

Anyone can:
- ✅ Access the evaluation tool
- ✅ Submit AI responses
- ✅ View detailed analysis
- ✅ Test all features

---

## Environment Variables Reference

### Vercel (Frontend)

| Variable | Value | Required |
|----------|-------|----------|
| `VITE_API_BASE` | `https://nl-gpt-azzfyfpjss6xw5tsgo6lc.streamlit.app` | ✅ Yes |

### Streamlit (Backend)

| Variable | Value | Required |
|----------|-------|----------|
| `MOCK_MODE` | `false` | ✅ Yes |
| `GROQ_API_KEY` | `gsk_your_key` | ✅ Yes |
| `CORS_ORIGINS` | `https://your-app.vercel.app,...` | ✅ Yes |

---

## Success Checklist

- [ ] Frontend deployed to Vercel
- [ ] `VITE_API_BASE` set to Streamlit URL
- [ ] Streamlit `CORS_ORIGINS` updated
- [ ] Frontend loads without errors
- [ ] Evaluation works end-to-end
- [ ] Shared URL with others

---

## Cost

| Service | Cost |
|---------|------|
| **Vercel** | Free (generous free tier) |
| **Streamlit** | Free (already deployed) |
| **Groq API** | Free (rate limited) |
| **Total** | **$0** 🎉 |

---

**Your frontend will be live on Vercel in 5 minutes!** 🚀

**Questions?** Check [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed guide.
