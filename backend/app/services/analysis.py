"""Phase 3 — Response Analysis Layer.

Explicitly extracts structured artifacts from AI responses:
- Atomic claims with span offsets
- Implicit assumptions linked to claims
- Ordered reasoning steps supporting claims
- Unsupported statements
- Completeness notes

Feeds Phase 3.5 Source Attribution Engine.
"""

from __future__ import annotations

import json
import logging
import re
from hashlib import sha256

from app.config import Settings, get_settings
from app.models.analysis import AnalysisResult, Assumption, Claim, ReasoningStep, TextSpan
from app.models.enums import ClaimType
from app.models.request import EvaluationRequest

logger = logging.getLogger(__name__)

MAX_CLAIMS = 25
DEDUPE_THRESHOLD = 0.92


def _preprocess_response(text: str) -> str:
    """Strip zero-width chars and normalize newlines."""
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _simple_string_similarity(a: str, b: str) -> float:
    """Jaccard similarity for deduplication."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def _deduplicate_claims(claims: list[dict]) -> list[dict]:
    """Remove near-duplicate claims using string similarity."""
    if len(claims) <= 1:
        return claims

    unique = [claims[0]]
    for claim in claims[1:]:
        is_duplicate = False
        for existing in unique:
            sim = _simple_string_similarity(claim["text"], existing["text"])
            if sim >= DEDUPE_THRESHOLD:
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(claim)

    return unique[:MAX_CLAIMS]


def _align_span_to_text(text: str, claim_text: str) -> TextSpan | None:
    """Find the position of claim_text in the original response."""
    if not claim_text or not text:
        return None

    pos = text.find(claim_text)
    if pos == -1:
        # Try case-insensitive
        pos = text.lower().find(claim_text.lower())

    if pos == -1:
        return None

    return TextSpan(start=pos, end=pos + len(claim_text))


async def _extract_with_llm(
    request: EvaluationRequest,
    settings: Settings,
) -> AnalysisResult:
    """Extract claims, assumptions, and reasoning steps using LLM."""
    from app.adapters.groq_client import create_groq_client

    client = create_groq_client(settings)

    system_prompt = (
        "You are an extraction engine. Output ONLY valid JSON. "
        "Extract claims, assumptions, and reasoning steps explicitly from the AI response.\n\n"
        "RULES:\n"
        "1. List every CLAIM as a standalone sentence (factual, opinion, or prediction)\n"
        "2. List every ASSUMPTION and link it to related claim IDs\n"
        "3. Build REASONING_STEPS in order (3-4+ steps), each with supports_claim_ids\n"
        "4. List UNSUPPORTED_STATEMENTS verbatim from the response\n"
        "5. Write COMPLETENESS_NOTES in plain language (no ratings or scores)\n\n"
        "CRITICAL: No numeric scores, confidence values, or quality ratings anywhere."
    )

    user_content = (
        f"User Query: {request.user_query}\n\n"
        f"AI Response:\n{request.ai_response}\n\n"
        f"Return JSON with this exact schema:\n"
        "{\n"
        '  "claims": [{"id": "c1", "text": "...", "type": "factual|opinion|prediction"}],\n'
        '  "assumptions": [{"id": "a1", "text": "...", "related_claim_ids": ["c1"], "derived_from_hint": "..."}],\n'
        '  "reasoning_steps": [{"id": "r1", "step": "...", "order": 1, "supports_claim_ids": ["c1"]}],\n'
        '  "unsupported_statements": ["..."],\n'
        '  "completeness_notes": "..."\n'
        "}"
    )

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model_analysis,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        # Build AnalysisResult from LLM output
        claims_data = data.get("claims", [])
        claims_data = _deduplicate_claims(claims_data)

        claims = []
        for i, c in enumerate(claims_data):
            claim_id = c.get("id", f"c{i+1}")
            claim_text = c.get("text", "")
            span = _align_span_to_text(request.ai_response, claim_text)
            claim_type = c.get("type", "factual")

            claims.append(
                Claim(
                    id=claim_id,
                    text=claim_text,
                    span=span,
                    type=ClaimType(claim_type),
                )
            )

        assumptions = [
            Assumption(
                id=a.get("id", f"a{i+1}"),
                text=a.get("text", ""),
                related_claim_ids=a.get("related_claim_ids", []),
                derived_from_hint=a.get("derived_from_hint"),
            )
            for i, a in enumerate(data.get("assumptions", []))
        ]

        reasoning_steps = [
            ReasoningStep(
                id=r.get("id", f"r{i+1}"),
                step=r.get("step", ""),
                order=r.get("order", i + 1),
                supports_claim_ids=r.get("supports_claim_ids", []),
            )
            for i, r in enumerate(data.get("reasoning_steps", []))
        ]

        # If no claims extracted, create synthetic summary claim
        if not claims:
            claims.append(
                Claim(
                    id="c1",
                    text=request.ai_response[:200],
                    span=TextSpan(start=0, end=min(200, len(request.ai_response))),
                    type=ClaimType.OPINION,
                )
            )

        return AnalysisResult(
            claims=claims,
            assumptions=assumptions,
            reasoning_steps=reasoning_steps,
            unsupported_statements=data.get("unsupported_statements", []),
            completeness_notes=data.get("completeness_notes", ""),
        )

    except Exception as exc:
        logger.error("LLM extraction failed: %s", exc)
        raise


def _build_fallback_analysis(request: EvaluationRequest) -> AnalysisResult:
    """Fallback extraction when LLM is unavailable."""
    sentences = re.split(r'(?<=[.!?])\s+', request.ai_response)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    claims = []
    for i, sentence in enumerate(sentences[:5]):
        pos = request.ai_response.find(sentence)
        span = TextSpan(start=pos, end=pos + len(sentence)) if pos != -1 else None

        claims.append(
            Claim(
                id=f"c{i+1}",
                text=sentence,
                span=span,
                type=ClaimType.FACTUAL,  # Changed from OPINION to FACTUAL for verification
            )
        )

    return AnalysisResult(
        claims=claims,
        assumptions=[],
        reasoning_steps=[],
        unsupported_statements=[],
        completeness_notes="Fallback extraction used; limited detail available.",
    )


async def analyze(request: EvaluationRequest) -> AnalysisResult:
    """Phase 3: Extract claims, assumptions, reasoning steps from AI response.

    Uses LLM extraction when available, falls back to rule-based extraction.
    Results are cached by hashing (ai_response, user_query).
    """
    settings = get_settings()

    if settings.mock_mode or not settings.effective_llm_api_key:
        return _build_fallback_analysis(request)

    try:
        return await _extract_with_llm(request, settings)
    except Exception as exc:
        logger.warning("LLM extraction failed, using fallback: %s", exc)
        return _build_fallback_analysis(request)
