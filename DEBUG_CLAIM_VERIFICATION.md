# 🔍 DEBUG: Claim Verification Not Working

## 🎯 The Problem

Claims show "No sufficient evidence found in provided sources" even though auto-search should find sources.

---

## 🔧 I've Added Detailed Logging

I just added **comprehensive logging** to the orchestrator. After Railway deploys, you'll see EXACTLY what's happening at each step.

---

## 📋 How to Debug

### Step 1: Wait for Railway to Deploy

1. Go to [Railway](https://railway.app)
2. Click your project → **Deployments**
3. Wait for latest deployment to show **"Success"**
4. This takes 2-3 minutes

### Step 2: Run an Evaluation

1. Go to your Vercel app: `https://nl-gpt13.vercel.app`
2. **Hard refresh:** `Ctrl + Shift + R`
3. Enter question: "Who is the Prime Minister of India?"
4. Enter AI response about Narendra Modi
5. **Check "Enable claim verification"** ✅
6. Click "Evaluate"
7. Wait 5-10 seconds

### Step 3: Check Railway Logs

1. Go to Railway → **Deployments** → **Latest** → **View Logs**
2. **Look for these log lines:**

```
🔍 Auto-searching for web sources...
📋 Extracted X claims to verify
✅ Found X web sources
  Source 1: Wikipedia - Narendra Modi - https://...
  Source 2: PMO India - Official Website - https://...
  Added citation 1: Wikipedia - Narendra Modi
  Added citation 2: PMO India - Official Website
📎 Total citations now: X

🔬 Phase 3: Analyzing response...
📊 Found X claims in analysis

🔗 Phase 3.5: Building attribution chains with X citations...
✅ Attribution complete: X chains built

📈 Phase 4: Evaluating...
✅ Evaluation complete: X claims evaluated
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Skipping auto-search"

**Log shows:**
```
⏭️ Skipping auto-search: enable_web_search=False, claim_verification=True
```

**Solution:**
1. Go to Railway → Your Service → **Variables**
2. Set `ENABLE_WEB_SEARCH=true`
3. Save (Railway will redeploy)

---

### Issue 2: "No web sources found"

**Log shows:**
```
🔍 Auto-searching for web sources...
📋 Extracted 3 claims to verify
⚠️ No web sources found!
```

**Solution:**
The web search service isn't finding sources. Check:

1. **Is the claim about a person?**
   - Should find Wikipedia
   - Check entity extraction in `web_search.py`

2. **Is the claim about numbers/prices?**
   - Should find SquareYards, MagicBricks
   - Check numerical detection

3. **Is the claim recent (2024, 2025)?**
   - Should find news outlets
   - Check recent news search

---

### Issue 3: "Found sources but no citations added"

**Log shows:**
```
✅ Found 5 web sources
  Source 1: Wikipedia - Narendra Modi
📎 Total citations now: 0
```

**Solution:**
The citations aren't being added to the request. This is a bug - screenshot the logs and share.

---

### Issue 4: "Citations added but claims still yellow"

**Log shows:**
```
✅ Found 5 web sources
📎 Total citations now: 5
🔗 Phase 3.5: Building attribution chains with 5 citations...
✅ Attribution complete: 3 chains built
```

**But claims still show:** "No sufficient evidence found"

**Solution:**
The attribution engine isn't using the citations properly. This should be fixed by the latest code, but if it persists:

1. Screenshot the full Railway logs
2. Share them for debugging

---

## 📊 Expected Successful Flow

**What you SHOULD see:**

```
🔍 Auto-searching for web sources...
📋 Extracted 3 claims to verify
✅ Found 5 web sources
  Source 1: Wikipedia - Narendra Modi - https://en.wikipedia.org/wiki/Narendra_Modi
  Source 2: PMO India - Official Website - https://www.pmindia.gov.in
  Source 3: Government of India Portal - https://www.india.gov.in
  Source 4: The Hindu - Latest News - https://www.thehindu.com
  Source 5: Times of India - News - https://timesofindia.indiatimes.com
  Added citation 1: Wikipedia - Narendra Modi
  Added citation 2: PMO India - Official Website
  Added citation 3: Government of India Portal
  Added citation 4: The Hindu - Latest News
  Added citation 5: Times of India - News
📎 Total citations now: 5

🔬 Phase 3: Analyzing response...
📊 Found 3 claims in analysis

🔗 Phase 3.5: Building attribution chains with 5 citations...
  → Claim c1: "Narendra Modi is Prime Minister"
     Using citation: Wikipedia - Narendra Modi
     Evidence: "Biographical information about Narendra Modi"
     Status: VERIFIED ✅
  → Claim c2: "Held office since May 2014"
     Using citation: Wikipedia
     Evidence: "Historical data about tenure"
     Status: VERIFIED ✅
  → Claim c3: "Third term on 9 June 2024"
     Using citation: The Hindu
     Evidence: "News coverage of 2024 election"
     Status: VERIFIED ✅
✅ Attribution complete: 3 chains built

📈 Phase 4: Evaluating...
  Claim c1: VERIFIED with 2 sources
  Claim c2: VERIFIED with 1 source
  Claim c3: VERIFIED with 2 sources
✅ Evaluation complete: 3 claims evaluated
```

**Result:** All claims turn **GREEN** 🟢 with sources listed!

---

## 🔍 What Each Log Line Means

| Log Line | Meaning |
|----------|---------|
| `🔍 Auto-searching...` | Auto-search is enabled and running ✅ |
| `📋 Extracted X claims` | Claims were extracted from AI response ✅ |
| `✅ Found X web sources` | Web search found authoritative sources ✅ |
| `Source 1: Wikipedia` | Specific source found ✅ |
| `Added citation X` | Citation added to request ✅ |
| `📎 Total citations now: X` | Citations are in the request ✅ |
| `⏭️ Skipping auto-search` | Auto-search is disabled OR claim verification disabled ❌ |
| `⚠️ No web sources found` | Web search didn't find any sources ❌ |

---

## 🚨 If Logs Show Success But Claims Still Yellow

This means the **frontend isn't displaying** the verification results correctly.

### Solution:

1. **Hard refresh browser:** `Ctrl + Shift + R`
2. **Clear cache:** `F12` → Right-click refresh → "Empty Cache and Hard Reload"
3. **Check browser console:** `F12` → Console tab → Look for errors
4. **Try incognito mode:** Open new incognito window and test

---

## 📋 Share These Logs With Me

If it's still not working after Railway deploys:

1. Go to Railway → Deployments → Latest → **View Logs**
2. **Copy ALL log lines** (not just errors)
3. **Share them** so I can see exactly what's happening

The logs will show:
- ✅ If auto-search ran
- ✅ If sources were found
- ✅ If citations were added
- ✅ If attribution used citations
- ✅ If claims were verified
- ✅ Where the failure occurred

---

## ✅ Quick Test After Deployment

After Railway deploys (2-3 minutes):

1. **Hard refresh** your Vercel app
2. **Run evaluation** with Narendra Modi example
3. **Check Railway logs** - should see all the ✅ lines above
4. **Check Vercel UI** - claims should be GREEN

If logs show ✅ but UI shows yellow:
- **Browser cache issue** - clear cache
- **Frontend bug** - share logs for debugging

---

## 🎯 Summary

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Railway deploys | Logs show detailed messages |
| 2 | Run evaluation | Auto-search triggers |
| 3 | Check logs | See "✅ Found X web sources" |
| 4 | Check logs | See "📎 Total citations now: X" |
| 5 | Check logs | See "Status: VERIFIED ✅" |
| 6 | Check UI | Claims turn GREEN 🟢 |

---

**Wait 2-3 minutes for Railway to deploy, then run an evaluation and share the Railway logs!**

The logs will tell us EXACTLY what's wrong and where to fix it! 🔍
