# 🔍 Railway Backend Testing Guide

## Understanding the "Detail Not Found" Error

When you visit `https://nl-gpt-production.up.railway.app/` and see:
```json
{"detail": "Not Found"}
```

**This is NORMAL!** ✅

FastAPI backends don't have a route for the root `/` by default. The API endpoints are at different paths.

---

## ✅ Test the Correct Endpoints

### 1. Health Check (Should Work)

**URL:**
```
https://nl-gpt-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "mock_mode": false,
  "llm_provider": "groq"
}
```

**If you see this:** ✅ Backend is working perfectly!

---

### 2. API Documentation (Swagger UI)

**URL:**
```
https://nl-gpt-production.up.railway.app/docs
```

**Expected:** Interactive API documentation page where you can test all endpoints.

---

### 3. Alternative API Docs (ReDoc)

**URL:**
```
https://nl-gpt-production.up.railway.app/redoc
```

**Expected:** Alternative API documentation with better readability.

---

### 4. Evaluate Endpoint (POST only)

**URL:**
```
https://nl-gpt-production.up.railway.app/api/v1/evaluate
```

**Expected if you just visit:** `405 Method Not Allowed` (because it needs POST request)

**This is correct!** The frontend will call this with a POST request.

---

## 🧪 How to Test from Browser

### Test 1: Health Endpoint

1. Open browser
2. Visit: `https://nl-gpt-production.up.railway.app/health`
3. Should see JSON response ✅

### Test 2: API Docs

1. Visit: `https://nl-gpt-production.up.railway.app/docs`
2. Should see Swagger UI ✅
3. Try clicking on `/api/v1/evaluate` → "Try it out"
4. Fill in the request body
5. Click "Execute"
6. See the response!

---

## 🔧 Using PowerShell to Test

### Test Health Endpoint

```powershell
Invoke-WebRequest -Uri "https://nl-gpt-production.up.railway.app/health" -Method GET
```

**Expected output:**
```
StatusCode        : 200
StatusDescription : OK
Content           : {"status":"ok","mock_mode":false,"llm_provider":"groq"}
```

### Test Evaluate Endpoint (requires POST)

```powershell
$body = @{
    user_query = "Test query"
    ai_response = "Test response"
    criteria = @("claim_verification", "source_transparency", "logic_reasoning", "missing_factors", "improve_answer_quality")
    claim_verification_enabled = $false
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://nl-gpt-production.up.railway.app/api/v1/evaluate" -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Expected Responses Summary

| URL | Method | Expected Response |
|-----|--------|-------------------|
| `/` | GET | `{"detail": "Not Found"}` ✅ (normal - no root route) |
| `/health` | GET | `{"status": "ok", ...}` ✅ (should work!) |
| `/docs` | GET | Swagger UI page ✅ |
| `/redoc` | GET | ReDoc page ✅ |
| `/api/v1/evaluate` | GET | `405 Method Not Allowed` ✅ (needs POST) |
| `/api/v1/evaluate` | POST | Evaluation results ✅ |

---

## ✅ Your Backend Status

Based on what you've told me:

- ✅ Railway backend is deployed
- ✅ Public domain is working
- ✅ Uvicorn server is running
- ✅ `/health` endpoint returns 200 OK
- ✅ MOCK_MODE = false
- ✅ GROQ_API_KEY is configured

**Your backend is working correctly!** 🎉

The "detail not found" on root URL is **expected behavior** for this API.

---

## 🎯 Next Step: Connect Vercel Frontend

Now that Railway is working:

1. **Update Vercel Environment Variable:**
   - Go to Vercel → Settings → Environment Variables
   - Set `VITE_API_BASE` = `https://nl-gpt-production.up.railway.app`

2. **Update Railway CORS:**
   - Go to Railway → Variables
   - Add `CORS_ORIGINS` = `https://nl-gpt13.vercel.app`

3. **Redeploy Vercel:**
   - Go to Deployments → Redeploy

4. **Test:**
   - Open `https://nl-gpt13.vercel.app`
   - Try an evaluation
   - Should work! ✅

---

## 🐛 If /health Also Shows "Detail Not Found"

If `/health` also returns 404, then there's a routing issue. Check:

### 1. Root Directory

Railway → Settings → Source → **Root Directory** should be:
```
backend
```

### 2. Procfile

Make sure `backend/Procfile` exists and contains:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Check Logs

Railway → Deployments → View Logs

Look for:
- ✅ "Uvicorn running on..." (good)
- ❌ "Error loading ASGI app" (bad - module import error)

---

## 📝 Quick Test URLs

Copy and paste these into your browser:

**Health Check:**
```
https://nl-gpt-production.up.railway.app/health
```

**API Documentation:**
```
https://nl-gpt-production.up.railway.app/docs
```

**Alternative Docs:**
```
https://nl-gpt-production.up.railway.app/redoc
```

---

## ✅ Success Indicators

Your backend is ready for Vercel when:

- [x] Railway public domain works
- [x] `/health` returns JSON with "status": "ok"
- [x] `/docs` shows Swagger UI
- [x] No errors in Railway logs
- [x] CORS_ORIGINS includes Vercel URL

---

**The "detail not found" on root URL is normal! Test `/health` instead.** 🎯

Let me know what `/health` returns!
