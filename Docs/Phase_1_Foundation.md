# Phase 1 — Foundation & Data Model

**Goal:** Establish project skeleton, shared schemas, configuration, and API contracts so later phases plug in without rework.

**Exit criteria:** `POST /api/v1/evaluate` returns a **valid mock** payload matching the final contract; frontend can render empty panel shell from types.

---

## 1.1 Deliverables

- Monorepo or two-folder layout (`frontend/`, `backend/`) per [Architecture Overview](./Architecture_Overview.md).
- Pydantic models + TypeScript types generated or mirrored manually.
- FastAPI app with health check, CORS, env validation.
- `.env.template` with `LLM_API_KEY`, `LLM_MODEL`, optional `SEARCH_API_KEY`.
- Docker Compose (optional) for local API + DB.

---

## 1.2 Core domain objects

### `EvaluationRequest`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `user_query` | string | no | Original user prompt |
| `ai_response` | string | **yes** | Text to evaluate |
| `conversation_id` | string | no | For memory-backed context |
| `criteria` | `Criteria[]` | **yes** | All 5 dimensions (panel always shows full set) |
| `claim_verification_enabled` | boolean | **yes** | Default `false`; when `true`, run verification + UI highlights |
| `source_preferences` | `SourcePreferences` | **yes** | Boolean toggles per category |
| `custom_sources` | `CustomSource[]` | no | User-added URLs/text |
| `user_context` | `UserContext` | no | Upload refs, pasted links |
| `citations` | `Citation[]` | no | If ChatGPT provided sources |
| `regenerate` | boolean | no | Default true if `improve_answer_quality` in criteria |
| `answer_quality_intent` | `AnswerQualityIntent` | no | User inputs for dimension 5; strongly recommended before regenerate |

### `Criteria` enum

```
claim_verification
source_transparency
logic_reasoning
missing_factors
improve_answer_quality
```

### `SourcePreferences`

```json
{
  "memory": true,
  "user_context": true,
  "web": true,
  "research": true,
  "company": true,
  "internal": true
}
```

### `EvaluationResponse` (top-level)

```json
{
  "evaluation_id": "uuid",
  "status": "completed",
  "analysis": { /* AnalysisResult — Phase 3 */ },
  "attribution": { /* AttributionResult — Phase 3.5 */ },
  "evaluation": { /* EvaluationResult — Phase 4; no numeric scores */ },
  "regeneration": { /* RegenerationResult | null */ },
  "meta": {
    "model": "gpt-4o",
    "duration_ms": 12000,
    "claim_verification_enabled": false,
    "dimensions": ["claim_verification", "source_transparency", "logic_reasoning", "missing_factors", "improve_answer_quality"]
  }
}
```

---

## 1.3 Analysis artifact (`AnalysisResult`)

Produced by Phase 3; defined here for contract stability.

```json
{
  "claims": [
    {
      "id": "c1",
      "text": "Bangalore is likely the strongest market.",
      "span": { "start": 120, "end": 165 },
      "type": "factual | opinion | prediction"
    }
  ],
  "assumptions": [
    {
      "id": "a1",
      "text": "Store demand correlates with social media engagement.",
      "related_claim_ids": ["c1"]
    }
  ],
  "reasoning_steps": [
    {
      "id": "r1",
      "step": "Demand appears strong.",
      "order": 1,
      "supports_claim_ids": ["c1"]
    }
  ],
  "unsupported_statements": ["..."],
  "completeness_notes": "..."
}
```

**Span indices:** UTF-16 or UTF-8 code unit policy must be documented in README; recommend **character offset in Unicode code points** for JS compatibility.

---

## 1.4 Attribution artifact (`AttributionResult`)

Produced by Phase 3.5. See [`Phase_3_5_Source_Attribution.md`](./Phase_3_5_Source_Attribution.md).

```json
{
  "chains": [
    {
      "claim_id": "c1",
      "claim_text": "Users prefer convenience.",
      "reasoning_step": { "step_id": "r1", "text": "..." },
      "source": { "label": "Survey Question 7", "source_type": "research", "url": null },
      "evidence": {
        "supporting": [{ "text": "73% respondents selected convenience" }],
        "counter": [{ "text": "19% selected price" }]
      },
      "assumption": {
        "text": "Users prefer convenience.",
        "derived_from": "Survey Question 7",
        "supporting_evidence": "73% respondents selected convenience",
        "counter_evidence": "19% selected price"
      },
      "attribution_gap": null
    }
  ]
}
```

---

## 1.5 Evaluation artifact (`EvaluationResult`)

**No scoring:** no `confidence`, percentages, 1–5 scales, or ranked numeric quality fields.

`claims[]` verification block is **omitted or empty** unless `claim_verification_enabled` was true on the request.

```json
{
  "claims": [
    {
      "claim_id": "c1",
      "status": "verified | needs_verification | unsupported | not_applicable",
      "sources": [
        {
          "title": "...",
          "url": "https://...",
          "source_type": "web | research | company | user_context | memory | internal | custom",
          "snippet": "..."
        }
      ],
      "verification_note": "Short reason for needs_verification"
    }
  ],
  "source_analysis": {
    "sources_used": [ /* grouped by type */ ],
    "trust_issues": ["..."],
    "missing_source_types": ["research"]
  },
  "logic": {
    "conclusion": "...",
    "reasoning_path": [
      {
        "step_id": "r1",
        "text": "Demand appears strong.",
        "evidence_links": [{ "url": "...", "label": "..." }],
        "expandable_detail": "Optional longer evidence block"
      }
    ],
    "logical_gaps": ["..."],
    "alternate_perspectives": ["..."],
    "critique": "..."
  },
  "missing_factors": [
    {
      "heading": "Competitor Analysis",
      "summary": "No evaluation of nearby competitors."
    }
  ],
  "answer_quality": {
    "clarity_note": "Structure is clear but jargon-heavy in paragraph 2.",
    "completeness_note": "Does not address cannibalization.",
    "actionability_note": "User cannot decide without rent assumptions.",
    "summary": "..."
  }
}
```

**Highlight rules (for UI):**

| `status` | Color token | Hover content |
|----------|-------------|---------------|
| `verified` | `highlight-verified` (pastel green) | 1–3 source links + short justification |
| `needs_verification` | `highlight-pending` (pastel yellow) | Short reason; optional “verify” links |
| `unsupported` | optional red tint in v2 | Reason only |

---

## 1.6 Regeneration artifact (`RegenerationResult`)

```json
{
  "improved_answer": "markdown or plain text",
  "changes_summary": [
    "Added competitor analysis section.",
    "Qualified demand claim with cited report."
  ],
  "recommended_inputs": [
    "Rent assumptions per sq ft",
    "List of competing brands in target micro-markets"
  ],
  "addressed_criteria": ["missing_factors", "claim_verification"]
}
```

### `AnswerQualityIntent` (request — dimension 5 input)

```json
{
  "user_intent": "Decide whether to open another SNITCH store in Bangalore.",
  "expertise_level": "intermediate",
  "user_goal": "Board-ready recommendation with risks called out.",
  "constraints_or_expectations": "Must use only cited survey data; under 500 words.",
  "good_answer_looks_like": "Executive summary, then pros/cons, then clear go/no-go criteria."
}
```

Regeneration (Phase 5) reads this object first when building the rewrite prompt.

---

## 1.7 Orchestrator interface

```python
# backend/app/orchestrator.py (conceptual)

async def run_evaluation(req: EvaluationRequest) -> EvaluationResponse:
    analysis = await analysis_service.analyze(req)
    attribution = await attribution_service.attribute(req, analysis)
    evaluation = await evaluation_service.evaluate(req, analysis, attribution)
    regeneration = None
    if Criteria.IMPROVE_ANSWER_QUALITY in req.criteria and req.regenerate:
        regeneration = await regeneration_service.regenerate(req, analysis, attribution, evaluation)
    return EvaluationResponse(...)
```

Claim verification runs inside `evaluate()` **only if** `req.claim_verification_enabled` is true.

**Idempotency:** Same `evaluation_id` returned only on explicit replay; new runs get new IDs.

---

## 1.8 Configuration

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | `openai` \| `anthropic` |
| `LLM_MODEL_ANALYSIS` | Cheaper/faster model for decomposition |
| `LLM_MODEL_EVAL` | Stronger model for judgment |
| `LLM_MODEL_REGEN` | Strongest model for rewrite |
| `MAX_RESPONSE_CHARS` | Truncate with user warning (e.g. 32k) |
| `MAX_CLAIMS` | Cap claims per run (e.g. 40) |
| `ENABLE_WEB_SEARCH` | Feature flag |

---

## 1.9 Testing (Phase 1)

- Contract tests: JSON Schema validation for mock fixtures.
- Golden files: `tests/fixtures/evaluate_response_snitch_example.json` based on problem statement Bangalore store scenario.

---

## 1.10 Tasks checklist

- [x] Initialize backend + frontend projects
- [x] Implement Pydantic models mirroring sections 1.2–1.5
- [x] Export TypeScript interfaces (`frontend/src/types/evaluation.ts`)
- [x] `GET /health`, `POST /evaluate` returning fixture
- [x] README: local setup, env vars, span index policy
