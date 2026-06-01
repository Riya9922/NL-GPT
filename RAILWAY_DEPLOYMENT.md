# Railway/Render Deployment Guide

## Quick Deploy

### Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Riya9922/NL-GPT)

**Steps:**
1. Click the button above
2. Set **Root Directory** to `backend` in Railway settings
3. Add environment variables (see below)
4. Deploy!

### Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Riya9922/NL-GPT)

**Steps:**
1. Click the button above
2. **Root Directory:** `backend`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see below)
6. Deploy!

---

## Environment Variables

Add these in Railway/Render dashboard:

```bash
# REQUIRED for production
MOCK_MODE=false

# Your Groq API key (get from console.groq.com)
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1

# LLM Configuration
LLM_PROVIDER=groq
LLM_MODEL_ANALYSIS=llama-3.1-8b-instant
LLM_MODEL_EVAL=llama-3.3-70b-versatile
LLM_MODEL_REGEN=llama-3.3-70b-versatile

# CORS - Allow your Vercel frontend
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app

# Optional: Web search
ENABLE_WEB_SEARCH=false

# Limits
MAX_RESPONSE_CHARS=32000
MAX_CLAIMS=40
```

---

## After Deployment

### 1. Get Backend URL
- Railway: `https://your-app.up.railway.app`
- Render: `https://your-app.onrender.com`

### 2. Test Health Endpoint
```bash
curl https://your-app.up.railway.app/health
```

Expected:
```json
{
  "status": "ok",
  "mock_mode": false,
  "llm_provider": "groq"
}
```

### 3. Deploy Frontend to Vercel
- Go to [vercel.com/new](https://vercel.com/new)
- Import from `Riya9922/NL-GPT`
- Set environment variable:
  ```bash
  VITE_API_BASE=https://your-app.up.railway.app
  ```
- Root directory: `frontend`
- Deploy!

---

## File Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── orchestrator.py      # Pipeline coordinator
│   ├── services/            # Business logic
│   └── adapters/            # LLM, search, storage
├── requirements.txt         # Python dependencies
├── Procfile                # Railway/Render start command
└── .env                    # Local environment (not committed)
```

---

## Troubleshooting

### Issue: "Port not available"
**Solution:** Railway/Render automatically sets `$PORT`. Don't hardcode a port.

### Issue: "Module not found"
**Solution:** Ensure Root Directory is set to `backend` in deployment settings.

### Issue: "CORS error from Vercel"
**Solution:** Add your Vercel URL to `CORS_ORIGINS`.

---

## Cost Estimate

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| **Railway** | $5 credit/month | $5-20/month |
| **Render** | 750 hours/month | $7-20/month |

Both offer excellent free tiers for testing!
