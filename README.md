# AI Output Evaluation Tool

[![Deploy Backend](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new)

Evaluate AI-generated responses across five dimensions with transparent attribution and optional answer improvement.

Architecture: [`Docs/00_Architecture_Index.md`](Docs/00_Architecture_Index.md)

## 🚀 Deployment

### Backend (Streamlit Cloud)

**Main file:** `streamlit_app.py`

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo: `Riya9922/NL-GPT`
3. Main file: `streamlit_app.py`
4. Add secrets (see [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)):
   ```toml
   MOCK_MODE = "false"
   GROQ_API_KEY = "gsk_your_key_here"
   CORS_ORIGINS = "https://your-vercel-app.vercel.app"
   ```
5. Deploy!

### Frontend (Vercel)

1. Import from `Riya9922/NL-GPT` at [vercel.com/new](https://vercel.com/new)
2. Set environment variable: `VITE_API_BASE=https://your-streamlit-app.streamlit.app`
3. Root directory: `frontend`
4. Deploy!

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for detailed instructions.

---

## Phase 1 status

- **Backend:** FastAPI + Pydantic models, `GET /health`, `POST /api/v1/evaluate` (mock SNITCH/Bangalore payload)
- **Frontend:** React + Vite + Tailwind, TypeScript types, expandable panel shell (all 5 dimensions, claim verification toggle, intent form)
- **Tests:** Contract tests + golden fixture `backend/tests/fixtures/evaluate_response_snitch_example.json`

## Span index policy

Claim `span.start` / `span.end` are **Unicode code point** offsets (Python `len()` on str, JavaScript `[...string].length`), not UTF-16 code units.

## Quick start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.template .env
# Add your Groq key to .env: GROQ_API_KEY=gsk_...
# Keep MOCK_MODE=true until Phases 3–5 (no API spend on evaluate)
uvicorn app.main:app --reload --port 8001
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the evaluation panel opens **expanded** with all five dimensions.

**If you see "Evaluate failed (500)":** the frontend could not reach the API. Start the backend first (command above). The UI and API must run together.

**Groq:** set `GROQ_API_KEY` in `backend/.env`. Use `MOCK_MODE=true` (default) for free mock responses; set `MOCK_MODE=false` when the live LLM pipeline is implemented. Test Groq: `GET http://127.0.0.1:8001/health/groq` (requires `MOCK_MODE=false` and a valid key).

**Port:** API runs on **8001** by default. The Vite dev proxy targets `http://127.0.0.1:8001`. Override with `frontend/.env`: `VITE_API_PROXY_TARGET=http://127.0.0.1:8000`

### Tests

```powershell
cd backend
python -m pytest tests/ -q
```

## API

`POST /api/v1/evaluate` — body must include:

- `ai_response` (required)
- `criteria` — all five: `claim_verification`, `source_transparency`, `logic_reasoning`, `missing_factors`, `improve_answer_quality`
- `claim_verification_enabled` — default `false`
- `source_preferences`, optional `answer_quality_intent`

See [`Docs/Phase_1_Foundation.md`](Docs/Phase_1_Foundation.md) for full schemas.
