# 🔧 Troubleshooting ModuleNotFoundError on Streamlit Cloud

## Current Error

```
ModuleNotFoundError: No module named 'app'
```

**Location:** `/mount/src/nl-gpt/streamlit_app.py:16`

---

## 🔍 Root Cause Analysis

The error occurs because Streamlit Cloud cannot find the `app` module in the Python path.

**Expected Structure:**
```
/mount/src/nl-gpt/
├── streamlit_app.py          # Entry point
├── backend/                   # ← app module is here
│   └── app/
│       ├── __init__.py
│       └── main.py
```

**Problem:** Streamlit runs from `/mount/src/nl-gpt/` but `app/` is in `/mount/src/nl-gpt/backend/app/`

---

## ✅ Solution Applied

Updated `streamlit_app.py` to:

1. **Use absolute paths** (not relative)
2. **Add debug logging** to see what paths are being used
3. **Insert backend path first** in sys.path

```python
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(script_dir, "backend")

# Add both paths to sys.path
sys.path.insert(0, backend_path)
sys.path.insert(0, script_dir)

# Debug: Print paths (will show in Streamlit logs)
print(f"[DEBUG] Script directory: {script_dir}")
print(f"[DEBUG] Backend path: {backend_path}")
print(f"[DEBUG] sys.path: {sys.path[:3]}")
```

---

## 🔍 How to Debug

### Step 1: Check Streamlit Logs

After pushing the latest commit, check the Streamlit Cloud logs for:

```
[DEBUG] Script directory: /mount/src/nl-gpt
[DEBUG] Backend path: /mount/src/nl-gpt/backend
[DEBUG] sys.path: ['/mount/src/nl-gpt/backend', '/mount/src/nl-gpt', ...]
```

### Step 2: Verify File Structure

In Streamlit Cloud dashboard, check the "Repository contents" section or use the terminal to verify:

```bash
ls -la /mount/src/nl-gpt/
ls -la /mount/src/nl-gpt/backend/
ls -la /mount/src/nl-gpt/backend/app/
```

**Expected output:**
```
/mount/src/nl-gpt/backend/app/
├── __init__.py
├── main.py
├── config.py
└── ...
```

### Step 3: Check Python Path

If the error persists, add this to `streamlit_app.py` **before** the import:

```python
import os
st.write("Current directory:", os.getcwd())
st.write("Directory contents:", os.listdir('.'))
st.write("Backend contents:", os.listdir('./backend') if os.path.exists('./backend') else "backend/ not found")
```

---

## 🛠️ Alternative Solutions

### Solution A: Move app/ to Root (Not Recommended)

Move the entire `backend/app/` directory to the root:

```bash
git mv backend/app ./app
```

**Pros:** Simple, works immediately  
**Cons:** Breaks backend structure, Railway deployment won't work

### Solution B: Use Relative Imports (Not Recommended)

Change imports to use relative paths:

```python
from backend.app.main import app
```

**Pros:** Explicit about location  
**Cons:** May not work with Streamlit's import system

### Solution C: Add Multiple Paths (Current Approach) ✅

Add both root and backend to sys.path:

```python
sys.path.insert(0, '/mount/src/nl-gpt/backend')
sys.path.insert(0, '/mount/src/nl-gpt')
```

**Pros:** Flexible, works with both structures  
**Cons:** Requires correct path resolution

---

## 📋 Verification Checklist

After deploying, verify:

- [ ] `streamlit_app.py` is in root: `/mount/src/nl-gpt/streamlit_app.py`
- [ ] `backend/` directory exists: `/mount/src/nl-gpt/backend/`
- [ ] `backend/app/` exists: `/mount/src/nl-gpt/backend/app/`
- [ ] `backend/app/__init__.py` exists
- [ ] `backend/app/main.py` exists
- [ ] Debug logs show correct paths
- [ ] `sys.path[0]` is `/mount/src/nl-gpt/backend`

---

## 🚨 Common Issues

### Issue 1: Streamlit hasn't pulled latest commit

**Symptom:** Still seeing old error messages

**Solution:** 
1. Wait 2-3 minutes for auto-refresh
2. Manually click "Rerun" in Streamlit dashboard
3. Check git commit hash in Streamlit logs

### Issue 2: backend/ directory not in git

**Symptom:** `backend/` folder doesn't exist on Streamlit

**Check:**
```bash
git ls-files | grep backend
```

**Solution:**
```bash
git add backend/
git commit -m "Add backend directory"
git push
```

### Issue 3: __init__.py missing

**Symptom:** Python doesn't recognize `backend/app/` as a package

**Check:**
```bash
ls backend/app/__init__.py
```

**Solution:**
```bash
touch backend/app/__init__.py
git add backend/app/__init__.py
git commit -m "Add __init__.py"
git push
```

### Issue 4: Wrong working directory

**Symptom:** `os.getcwd()` shows unexpected directory

**Solution:** Use absolute paths (already done in current code)

---

## 📊 Expected Behavior After Fix

Once the import works, you should see:

1. ✅ Streamlit dashboard loads
2. ✅ Status metrics display (Ready, Mock/Live, LLM Provider)
3. ✅ API documentation section visible
4. ✅ "Try It Now" expander works
5. ✅ No `ModuleNotFoundError` in logs

---

## 🔬 Manual Testing

Test locally to verify the fix:

```bash
cd /path/to/nl-gpt
python streamlit_app.py
```

Or use Streamlit:

```bash
streamlit run streamlit_app.py
```

Check that the debug output shows:
- Script directory: `/absolute/path/to/nl-gpt`
- Backend path: `/absolute/path/to/nl-gpt/backend`
- sys.path[0]: `/absolute/path/to/nl-gpt/backend`

---

## 📞 If Still Not Working

### Collect This Information:

1. **Check current commit:**
   ```bash
   git log --oneline -1
   ```

2. **Check Streamlit logs** for debug output:
   ```
   [DEBUG] Script directory: ???
   [DEBUG] Backend path: ???
   [DEBUG] sys.path: ???
   ```

3. **List directory contents:**
   ```bash
   ls -la /mount/src/nl-gpt/
   ls -la /mount/src/nl-gpt/backend/ 2>/dev/null || echo "backend/ not found"
   ```

4. **Check file permissions:**
   ```bash
   ls -la /mount/src/nl-gpt/backend/app/__init__.py
   ```

### Create GitHub Issue

If the error persists, create an issue with:
- Streamlit Cloud logs (with debug output)
- Git commit hash
- Directory listing output
- Full error traceback

---

## ✅ Current Status

**Latest commit:** `2dea56b` - Added debug logging to streamlit_app.py

**What's been done:**
- ✅ Used absolute paths (`os.path.abspath(__file__)`)
- ✅ Added debug logging
- ✅ Inserted backend path first in sys.path
- ✅ Verified backend structure is correct
- ✅ Committed and pushed to GitHub

**Next:** Wait for Streamlit Cloud to pull the latest commit and check the debug output in logs!

---

**🎯 The fix is in place. Streamlit Cloud should update within 2-3 minutes.**

**Check the logs for the `[DEBUG]` messages to confirm the paths are correct!**
