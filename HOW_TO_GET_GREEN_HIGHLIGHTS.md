# 🟢 How to Get Green Highlights (Verified Claims)

## Understanding Claim Verification

The tool uses **two colors** for claim verification:
- 🟢 **Green** = Claim is **verified** by sources you provided
- 🟡 **Yellow** = Claim **needs verification** (no source found)

---

## 🔧 How to Add Sources

### Step 1: Scroll Down to "Sources" Section

In the evaluation form, **scroll down** below the AI response field. You'll see a section called **"Sources"** with these options:

1. **Upload files** (.txt, .md, .pdf)
2. **Link URLs** ← **Use this for SquareYards!**
3. **Paste supporting context**
4. **Custom Sources**

---

## 📋 Add Your SquareYards Source

### Method 1: Link URL (Recommended)

1. **Click "+ Add URL"** button
2. **Paste the SquareYards URL:**
   ```
   https://www.squareyards.com/property-rates-in-mumbai
   ```
   (or whatever the actual SquareYards article URL is)

3. **The tool will fetch this URL** and use it as a source for verification

### Method 2: Paste Supporting Context

If you can't access the URL, copy the key information:

1. **Go to SquareYards article**
2. **Copy the relevant text** (e.g., "Mumbai average residential price is ₹38,600 per sq. ft...")
3. **Paste in "Paste supporting context" field:**
   ```
   Source: SquareYards - Property Rates in Mumbai (May 2026)
   
   As of 2026, Mumbai's average residential asking price is around ₹38,600 per sq. ft. 
   Prices range from under ₹15,000/sq. ft. in peripheral areas to over ₹1 lakh/sq. ft. 
   in premium South Mumbai neighborhoods.
   
   Key data points:
   - Average price: ₹38,600/sq. ft.
   - Low-end (peripheral areas): under ₹15,000/sq. ft.
   - High-end (South Mumbai): over ₹1 lakh/sq. ft.
   ```

### Method 3: Custom Sources

1. **Click "+ Add Custom Source"**
2. **Fill in:**
   - **Label:** `SquareYards Mumbai Property Rates`
   - **URL:** `https://www.squareyards.com/property-rates-in-mumbai`
   - **Notes:** `May 2026 property price trends for Mumbai`

---

## ✅ Complete Workflow Example

### Step 1: Enter Question and Response

**Your question:**
```
What are the current flat prices in Mumbai?
```

**AI response:**
```
Flat prices in Mumbai vary enormously by locality, building age, amenities, 
and connectivity. As of 2026, the city's average residential asking price is 
around ₹38,600 per sq. ft., but actual prices range from under ₹15,000/sq. ft. 
in some peripheral areas to over ₹1 lakh/sq. ft. in premium South Mumbai 
neighborhoods.
```

### Step 2: Add Source

**Scroll down to "Sources" section:**

**Option A - Link URL:**
```
https://www.squareyards.com/property-rates-in-mumbai
```

**Option B - Paste Context:**
```
Source: SquareYards - Property Rates in Mumbai (May 2026)

Average residential price: ₹38,600 per sq. ft.
Range: ₹15,000/sq. ft. (peripheral) to ₹1,00,000/sq. ft. (South Mumbai)
```

### Step 3: Enable Claim Verification

**Make sure this is checked:**
- ☑️ **Enable claim verification**

### Step 4: Click "Evaluate"

Wait 5-10 seconds.

---

## 🎯 Expected Result

### Before (No Source Provided):
```
Claim c1: "₹38,600 per sq. ft."
Status: 🟡 Needs verification
Note: No sufficient evidence found in provided sources.
```

### After (SquareYards Source Added):
```
Claim c1: "₹38,600 per sq. ft."
Status: 🟢 Verified
Source: SquareYards - Property Rates in Mumbai
Snippet: "Mumbai's average residential asking price is around ₹38,600 per sq. ft."
```

**The highlight in the AI response will turn GREEN!** 🎉

---

## 🔍 How Verification Works

### The Tool Checks:

1. **Does the claim match source information?**
   - Claim: "₹38,600 per sq. ft."
   - Source: "₹38,600 per sq. ft." ✅ → **Green (Verified)**

2. **Is the source credible?**
   - SquareYards is a real estate platform ✅
   - Claims about property prices from SquareYards are credible ✅

3. **Are there contradicting sources?**
   - If another source says "₹25,000/sq. ft." ❌ → **Red (Unsupported)**
   - If no contradiction ✅ → **Green (Verified)**

---

## 📊 What Each Status Means

| Status | Color | Meaning |
|--------|-------|---------|
| **Verified** | 🟢 Green | Claim is supported by sources you provided |
| **Needs Verification** | 🟡 Yellow | No source found to verify this claim |
| **Unsupported** | 🔴 Red | Sources contradict this claim |
| **Not Applicable** | ⚪ Gray | Opinion-based claim (no verification needed) |

---

## 🚀 Quick Test

### Try This Now:

1. **Question:**
   ```
   What are flat prices in Mumbai?
   ```

2. **AI Response:**
   ```
   Mumbai's average residential price is around ₹38,600 per sq. ft., 
   ranging from ₹15,000/sq. ft. in peripheral areas to over ₹1 lakh/sq. ft. 
   in South Mumbai.
   ```

3. **Add Source (Link URL):**
   ```
   https://www.squareyards.com/property-rates-in-mumbai
   ```

4. **Enable claim verification:** ☑️

5. **Click "Evaluate"**

6. **Expected Result:**
   - Claims turn **GREEN** 🟢
   - Source attribution shows SquareYards
   - Verification note: "Supported by SquareYards property data"

---

## 💡 Pro Tips

### Tip 1: Provide Multiple Sources

Add multiple URLs for better verification:
```
https://www.squareyards.com/property-rates-in-mumbai
https://www.magicbricks.com/property-price-trends-mumbai
https://www.99acres.com/property-rates-mumbai
```

### Tip 2: Be Specific in Pasted Context

**Bad:**
```
Mumbai has expensive property.
```

**Good:**
```
Source: SquareYards (May 2026)
Average: ₹38,600/sq. ft.
Range: ₹15,000-₹1,00,000/sq. ft.
```

### Tip 3: Enable All Source Types

In **Source Preferences**, keep all checked:
- ☑️ Memory
- ☑️ User-Provided Context ← **Important!**
- ☑️ Web Sources
- ☑️ Research Papers
- ☑️ Company Sources
- ☑️ Internal Knowledge

---

## ❌ Common Issues

### Issue 1: Still showing yellow after adding source

**Cause:** Source doesn't contain the specific claim data

**Solution:** Paste more specific information from the source

### Issue 2: URL not working

**Cause:** URL is blocked or requires login

**Solution:** Copy the text manually and use "Paste supporting context"

### Issue 3: Too many claims, not all verified

**Cause:** Some claims are opinions or not in sources

**Solution:** That's correct behavior - not all claims need verification

---

## ✅ Summary

| What You Want | What to Do |
|---------------|-----------|
| 🟡 Yellow → 🟢 Green | **Add the source URL or paste source text** |
| Verify price claims | **Add SquareYards URL** |
| Verify location claims | **Add source with location information** |
| See source attribution | **Add Custom Source with label + URL** |

---

**Add your SquareYards URL in the "Link URLs" field, and claims will turn green!** 🎯
