# 🌐 Automatic Web Search for Claim Verification

## ✨ New Feature: Auto-Source Discovery

The tool now **automatically searches the web** for authoritative sources to verify claims in AI responses!

---

## 🎯 How It Works

### When You Enable Claim Verification:

1. **Extract claims** from the AI response
2. **Auto-search the web** for relevant sources (if `enable_web_search=true`)
3. **Add sources as citations** automatically
4. **Verify claims** against these sources
5. **Highlight verified claims in GREEN** 🟢

---

## 📊 Example: Mumbai Flat Prices

### Before (Manual Sources Only):

**You enter:**
```
Question: What are flat prices in Mumbai?
AI Response: Mumbai's average price is ₹38,600 per sq. ft.

[No sources provided]
```

**Result:**
- Claim: "₹38,600 per sq. ft."
- Status: 🟡 **Needs verification** (no sources)

### After (Automatic Web Search):

**You enter:**
```
Question: What are flat prices in Mumbai?
AI Response: Mumbai's average price is ₹38,600 per sq. ft.

[No sources provided - but web search is enabled!]
```

**What Happens:**
1. System extracts claim: "₹38,600 per sq. ft."
2. Auto-searches web for: "Mumbai flat prices 2026"
3. **Finds sources:**
   - SquareYards - Property Rates
   - MagicBricks - Price Trends
   - 99acres - Property Rates
4. Adds these as citations automatically
5. Verifies claim against sources

**Result:**
- Claim: "₹38,600 per sq. ft."
- Status: 🟢 **Verified** (supported by SquareYards, MagicBricks, 99acres)
- **Highlight turns GREEN!** ✨

---

## 🔧 Configuration

### Enable/Disable Web Search

**In Railway Environment Variables:**
```bash
ENABLE_WEB_SEARCH=true
```

**Default:** `true` (enabled)

### How to Disable:

If you want to disable automatic web search:
```bash
ENABLE_WEB_SEARCH=false
```

---

## 🎯 What Types of Claims Get Auto-Verified?

### Numerical Claims (Prices, Statistics):
```
"Mumbai average is ₹38,600 per sq. ft."
↓ Auto-searches for:
- Real estate sources (SquareYards, MagicBricks, 99acres)
- Property price databases
```

### General Factual Claims:
```
"India's GDP grew by 7% in 2025"
↓ Auto-searches for:
- Government statistics portals
- Economic databases
- Official reports
```

### Location-Specific Claims:
```
"South Mumbai has premium property rates"
↓ Auto-searches for:
- Local real estate sources
- Regional property data
```

---

## 📊 Source Credibility

The system prioritizes **high-credibility sources:**

| Source Type | Examples | Credibility |
|-------------|----------|-------------|
| **Official Portals** | Government sites, NSE, RBI | 🟢 High |
| **Major Platforms** | SquareYards, MagicBricks, 99acres | 🟢 High |
| **News Outlets** | Economic Times, Moneycontrol | 🟡 Medium |
| **Wikipedia** | General knowledge | 🟡 Medium |
| **Blogs/Forums** | Personal opinions | 🔴 Low (not used) |

---

## 🚀 How to Use

### Step 1: Enable Claim Verification

In the evaluation form:
- ☑️ **Enable claim verification**

### Step 2: Submit Evaluation

**Click "Evaluate"**

The system will:
1. Extract claims from AI response
2. **Automatically search web** for sources
3. Add found sources as citations
4. Verify claims against sources
5. Show results with green/yellow highlights

### Step 3: See Results

**Verified Claim:**
```
Claim: "₹38,600 per sq. ft."
Status: 🟢 Verified
Sources: 
  - SquareYards: "Mumbai's average is ₹38,600/sq. ft."
  - MagicBricks: "Average price ₹38,600 per sq. ft."
```

**The highlight in the AI response turns GREEN!** 🎉

---

## 📋 What You'll See in Railway Logs

When automatic web search runs, you'll see:

```
🔍 Auto-searching for web sources...
✅ Found 3 web sources
  - SquareYards - Property Rates
  - MagicBricks - Property Price Trends
  - 99acres - Property Rates
```

---

## 🎯 Example Workflow

### Scenario: Evaluating Mumbai Property Prices

**Your Input:**
```
Question: What are current flat prices in Mumbai?

AI Response:
Flat prices in Mumbai vary enormously by locality. As of 2026, 
the city's average residential asking price is around ₹38,600 per 
sq. ft., but actual prices range from under ₹15,000/sq. ft. in 
some peripheral areas to over ₹1 lakh/sq. ft. in premium South 
Mumbai neighborhoods.
```

**Click "Evaluate" (with claim verification enabled)**

**What Happens:**
1. System extracts 3 claims:
   - c1: "Average price is ₹38,600 per sq. ft."
   - c2: "Prices range from under ₹15,000/sq. ft."
   - c3: "Premium areas over ₹1 lakh/sq. ft."

2. **Auto-search triggers:**
   ```
   🔍 Searching for: "Mumbai flat prices 2026 ₹38,600"
   🔍 Searching for: "Mumbai property rates 2026"
   ```

3. **Sources found:**
   - SquareYards (May 2026): "Average ₹38,600/sq. ft."
   - MagicBricks: "Range ₹15,000-₹1,00,000/sq. ft."
   - 99acres: "South Mumbai premium rates"

4. **Claims verified:**
   - c1: ✅ Matches SquareYards → **GREEN**
   - c2: ✅ Matches MagicBricks → **GREEN**
   - c3: ✅ Matches 99acres → **GREEN**

**Final Result:**
```
All claims highlighted in GREEN 🟢
Verification status: Verified
Sources: SquareYards, MagicBricks, 99acres
```

---

## 🔄 Manual vs Automatic Sources

### You Can Still Add Manual Sources:

**Link URLs:**
```
https://www.squareyards.com/property-rates-in-mumbai
```

**Paste Context:**
```
Source: RBI Report 2026
Mumbai property prices increased by 5%...
```

### Automatic + Manual = Best Results:

The system combines:
- ✅ **Auto-discovered sources** (web search)
- ✅ **Your manual sources** (URLs you add)
- ✅ **Both used for verification**

---

## 🎯 Benefits

| Before (Manual Only) | After (Automatic) |
|---------------------|-------------------|
| ❌ Must find sources yourself | ✅ System finds sources |
| ❌ Claims stay yellow | ✅ Claims turn green |
| ❌ Limited verification | ✅ Comprehensive verification |
| ❌ Time-consuming | ✅ Fast and automatic |

---

## 💡 Pro Tips

### Tip 1: Be Specific in Your Question

**Bad:**
```
Question: Flats
```

**Good:**
```
Question: What are current flat prices in Mumbai in 2026?
```

The more specific, the better the auto-search results!

### Tip 2: Enable All Source Types

In **Source Preferences**, keep all checked:
- ☑️ Memory
- ☑️ User-Provided Context
- ☑️ **Web Sources** ← Important for auto-search!
- ☑️ Research Papers
- ☑️ Company Sources
- ☑️ Internal Knowledge

### Tip 3: Check Railway Logs

If auto-search isn't working:
1. Go to Railway → Deployments → View Logs
2. Look for: `🔍 Auto-searching for web sources...`
3. If missing, web search might be disabled

---

## 🐛 Troubleshooting

### Issue: Claims still yellow after auto-search

**Possible causes:**
1. Web search disabled (`ENABLE_WEB_SEARCH=false`)
2. No authoritative sources found
3. Claim is opinion-based (not verifiable)

**Solution:**
- Check Railway logs for web search activity
- Manually add sources if auto-search doesn't find them
- Verify claim is factual, not opinion

### Issue: Wrong sources being used

**Possible cause:** Claim keywords match wrong sources

**Solution:**
- Add manual sources with specific URLs
- Make your question more specific

---

## ✅ Summary

| Feature | Status |
|---------|--------|
| **Automatic web search** | ✅ Enabled by default |
| **Auto-source discovery** | ✅ Works for numerical claims |
| **Claim verification** | ✅ Uses auto-found sources |
| **Green highlights** | ✅ Shows verified claims |

---

**Just enable claim verification and the tool will automatically find sources and turn verified claims GREEN!** 🎉

No manual source entry needed - it's all automatic now!
