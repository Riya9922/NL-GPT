# Streamlit Cloud Deployment Guide

## 📋 Main File Path

**Main file for Streamlit:** `streamlit_app.py`

This is the entry point that Streamlit Cloud will run.

---

## 🚀 Deployment Steps

### Step 1: Connect Repository

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account (if not already connected)
4. Select repository: **`Riya9922/NL-GPT`**
5. Branch: **`main`**
6. Main file path: **`streamlit_app.py`**

### Step 2: Configure Secrets

Click **"Advanced settings"** → **"Secrets"** and add:

```toml
# REQUIRED: Disable mock mode for production
MOCK_MODE = "false"

# REQUIRED: Your Groq API key
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# LLM Configuration
LLM_PROVIDER = "groq"
LLM_MODEL_ANALYSIS = "llama-3.1-8b-instant"
LLM_MODEL_EVAL = "llama-3.3-70b-versatile"
LLM_MODEL_REGEN = "llama-3.3-70b-versatile"

# CORS - Allow your Vercel frontend
CORS_ORIGINS = "https://your-app.vercel.app,https://your-app-git-main.vercel.app,https://your-app.vercel.app"

# Optional: Web search
ENABLE_WEB_SEARCH = "false"

# Limits
MAX_RESPONSE_CHARS = "32000"
MAX_CLAIMS = "40"
```

### Step 3: Deploy

1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. Your app will be available at: `https://your-app-name.streamlit.app`

### Step 4: Get Backend URL

After deployment, copy your Streamlit app URL (e.g., `https://nl-gpt-backend.streamlit.app`)

You'll need this for the frontend deployment on Vercel.

---

## 🔧 Configuration Files

### `requirements.txt` (Root)
Lists all Python dependencies. Streamlit automatically installs these.

### `.streamlit/config.toml`
Streamlit server configuration (already configured).

### `.streamlit/secrets.toml.example`
Template for secrets (use this as reference).

---

## 📊 App Features

The Streamlit app provides:

- ✅ **API Dashboard** - Visual status of the backend
- ✅ **Health Metrics** - Monitor mode (mock/live) and LLM provider
- ✅ **API Documentation** - Quick reference for all endpoints
- ✅ **Example Code** - Ready-to-use API call examples
- ✅ **Configuration Guide** - Setup instructions for users

---

## 🔍 Testing the Deployment

### Test Health Endpoint
```bash
curl https://your-app-name.streamlit.app/health
```

Expected response:
```json
{
  "status": "ok",
  "mock_mode": false,
  "llm_provider": "groq"
}
```

### Test Evaluation Endpoint
```bash
curl -X POST https://your-app-name.streamlit.app/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Test query",
    "ai_response": "Test response",
    "criteria": ["claim_verification", "logic_reasoning"],
    "claim_verification_enabled": false
  }'
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution:** Ensure `requirements.txt` is in the root directory (it is).

### Issue: "GROQ_API_KEY not set"
**Solution:** Check that secrets are properly configured in Streamlit dashboard.

### Issue: "CORS error when calling from Vercel"
**Solution:** Update `CORS_ORIGINS` in secrets to include your Vercel app URL.

### Issue: "Server not starting"
**Solution:** Check Streamlit logs in the dashboard. Common causes:
- Missing required secrets
- Invalid API key
- Port conflict (rare on Streamlit Cloud)

---

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MOCK_MODE` | ✅ | `true` | Set to `false` for production |
| `GROQ_API_KEY` | ✅ (prod) | `""` | Your Groq API key |
| `LLM_PROVIDER` | ❌ | `groq` | LLM provider (groq/openai/anthropic) |
| `CORS_ORIGINS` | ✅ | `localhost` | Comma-separated allowed origins |
| `MAX_CLAIMS` | ❌ | `40` | Maximum claims to extract |

---

## 🔗 Connect Frontend

After deploying backend, deploy frontend to Vercel:

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import from `Riya9922/NL-GPT`
3. Set environment variable:
   ```bash
   VITE_API_BASE=https://your-streamlit-app.streamlit.app
   ```
4. Root directory: `frontend`
5. Deploy!

---

## 📞 Support

For issues:
- Check Streamlit Cloud docs: [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- Review logs in Streamlit dashboard
- Verify all secrets are set correctly
- Test API endpoints with curl/Postman first
