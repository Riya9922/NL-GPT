# Edge Cases & Quality Bar

Reference for phases 2–7. Use during implementation and QA.

---

## 1. Input edge cases

| Case | Expected behavior |
|------|-------------------|
| Empty AI response | 400 validation error |
| Response is only code block | Analyze code claims separately; note “code not executed” |
| Non-English text | Analyze in source language; UI labels stay English |
| >32k characters | Truncate with warning banner; evaluate first N chars |
| Markdown tables/images | Strip images; flatten tables to text for analysis |
| Multiple topics in one answer | Claims grouped; conclusion may be weak — logic module notes fragmentation |
| User selects 0 source types | Allow but warn: “Attribution limited to response text only” |
| Claim verification toggle off | No highlights; `evaluation.claims` empty; attribution chains still returned |
| All criteria not sent | 400 — API must receive all 5 dimension keys |

---

## 2. Claim & span edge cases

| Case | Expected behavior |
|------|-------------------|
| Claim text not found in response (paraphrase drift) | `span: null`; show claim in sidebar list not inline |
| Overlapping claims | Merge or prioritize highlight per Phase 6 rules |
| Duplicate claims | Deduplicate in post-process |
| Sarcasm / irony | Often `needs_verification` or opinion type |
| Statistical claims without numbers | Flag needs verification; missing factors suggest data |

---

## 3. Verification edge cases

| Case | Expected behavior |
|------|-------------------|
| Web search returns conflicting sources | `needs_verification` + note conflict |
| Search API down | Skip web; note in `source_analysis.trust_issues` |
| User disables `web` but enables verification | Use only user context + citations + custom |
| Citation URL 404 | Mark source untrustworthy; claim downgraded |
| Paywalled content | Snippet-only; note in `attribution_gap` or `verification_note` |
| Internal knowledge only | If `internal` false → cannot mark `verified` |

---

## 4. Reasoning edge cases

| Case | Expected behavior |
|------|-------------------|
| No clear conclusion | `conclusion` = “No single conclusion identified” |
| <3 reasoning steps possible | Return available steps; do not pad with fluff |
| Circular reasoning | `logical_gaps` explicitly calls out circularity |
| Ad hominem / fallacy | Mention in `critique` without moralizing |

---

## 5. Missing factors edge cases

| Case | Expected behavior |
|------|-------------------|
| Already comprehensive answer | Few or zero items; say “No major gaps detected” |
| Creative writing / fiction | Module skipped or returns not_applicable |
| Medical/legal questions | Add disclaimer: not professional advice |

---

## 6. Regeneration edge cases

| Case | Expected behavior |
|------|-------------------|
| No `improve_answer_quality` criterion | `regeneration: null` |
| `regenerate: false` | Skip; still show `recommended_inputs` if criteria includes improve |
| LLM adds new URL | Validator strips; warning in meta |
| Improved answer longer than limit | Truncate with “show more” |
| User re-runs with different sources | New `evaluation_id`; optional diff view (v2) |

---

## 7. UI edge cases

| Case | Expected behavior |
|------|-------------------|
| Very long response | Left column scroll independent of panel |
| No spans | Sidebar lists all claims with status chips |
| Hover on mobile | Tap to open popover; dismiss on outside tap |
| Color-only status | Icons + labels for colorblind users |
| Panel collapsed | Highlights still visible on main text |

---

## 8. Security edge cases

| Case | Expected behavior |
|------|-------------------|
| Malicious URL in custom source | SSRF block; show error on that source only |
| Prompt injection in AI response | System prompts treat response as untrusted data |
| PII in response | Avoid echoing PII in logs; optional redaction (v2) |
| File upload zip bomb | Size/MIME limits; reject |

---

## 9. Performance edge cases

| Case | Expected behavior |
|------|-------------------|
| 40+ claims | Cap at `MAX_CLAIMS`; note in meta |
| Repeated evaluate same text | Return cached analysis if within TTL |
| Concurrent evaluates | Queue or 429 per session |

---

## 10. Acceptance scenarios (from problem statement)

### Scenario A — SNITCH Bangalore

**Input:** Short recommendation to open Bangalore store.

**Must demonstrate:**

- Reasoning path with expandable evidence
- Assumptions list (demand ↔ social media, etc.)
- Missing: competitors, economics, cannibalization, saturation
- Optional regenerated answer addressing gaps

### Scenario B — Verified vs pending highlights

**Input:** Answer mixing firm facts and speculative statements.

**Must demonstrate:**

- Pastel green on verified spans with 1–3 links on hover
- Pastel yellow on needs verification with short reason

### Scenario C — Source toggles

**Input:** User unchecks Web before re-evaluate.

**Must demonstrate:**

- No web URLs in verified sources
- `missing_source_types` may suggest enabling web

---

## 11. Definition of done (project)

- [ ] All 5 criteria work independently and combined
- [ ] Panel matches section order in problem statement
- [ ] Highlights + hover rules implemented
- [ ] Regeneration respects citation whitelist
- [ ] Edge cases in sections 1–9 have automated or manual test coverage
- [ ] Deployed MVP with README quickstart
