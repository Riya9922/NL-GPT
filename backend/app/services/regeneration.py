"""Phase 5 — Regeneration Engine.

Produces an improved answer and summary of changes using evaluation findings,
respecting user source preferences and selected criteria.

NO fabricated sources — only cite URLs present in evaluation sources or user context.
"""

from __future__ import annotations

import json
import logging
import re

from app.config import Settings, get_settings
from app.models.analysis import AnalysisResult
from app.models.attribution import AttributionResult, ClaimAttributionChain
from app.models.enums import Criteria, SourceType
from app.models.evaluation import EvaluationResult
from app.models.regeneration import RegenerationResult
from app.models.request import AnswerQualityIntent, EvaluationRequest

logger = logging.getLogger(__name__)

MAX_CHANGES_BULLETS = 8
MAX_RECOMMENDED_INPUTS = 5


def _build_citation_whitelist(
    request: EvaluationRequest,
    attribution: AttributionResult,
    evaluation: EvaluationResult,
) -> set[str]:
    """Build whitelist of allowed citation URLs from evaluation sources."""
    allowed_urls: set[str] = set()

    # From citations in request
    for citation in request.citations:
        if citation.url:
            allowed_urls.add(citation.url)

    # From attribution chains
    for chain in attribution.chains:
        if chain.source and chain.source.url:
            allowed_urls.add(chain.source.url)

    # From evaluation sources
    for source_item in evaluation.source_analysis.sources_used:
        if source_item.url:
            allowed_urls.add(source_item.url)

    # From custom sources
    for custom in request.custom_sources:
        if custom.url:
            allowed_urls.add(custom.url)

    return allowed_urls


def _build_regeneration_packet(
    request: EvaluationRequest,
    analysis: AnalysisResult,
    attribution: AttributionResult,
    evaluation: EvaluationResult,
) -> dict:
    """Build comprehensive regeneration packet for LLM prompt."""
    # Original response (truncated if needed)
    original_response = request.ai_response
    if len(original_response) > 4000:
        original_response = original_response[:4000] + "\n...[truncated]"

    # User intent block
    intent_block = ""
    if request.answer_quality_intent:
        intent = request.answer_quality_intent
        intent_parts = []
        if intent.user_intent:
            intent_parts.append(f"User Intent: {intent.user_intent}")
        if intent.expertise_level:
            intent_parts.append(f"Expertise Level: {intent.expertise_level}")
        if intent.user_goal:
            intent_parts.append(f"Goal: {intent.user_goal}")
        if intent.constraints_or_expectations:
            intent_parts.append(f"Constraints: {intent.constraints_or_expectations}")
        if intent.good_answer_looks_like:
            intent_parts.append(f"Good Answer Looks Like: {intent.good_answer_looks_like}")
        intent_block = "\n".join(intent_parts)

    # Missing factors (heading + summary only)
    missing_factors_text = ""
    if evaluation.missing_factors:
        factors = "\n".join(
            f"- {mf.heading}: {mf.summary}"
            for mf in evaluation.missing_factors[:6]
        )
        missing_factors_text = f"\n\nMissing Factors to Address:\n{factors}"

    # Logical gaps and alternate perspectives
    logic_text = ""
    if evaluation.logic.logical_gaps:
        gaps = "\n".join(f"- {gap}" for gap in evaluation.logic.logical_gaps[:3])
        logic_text += f"\n\nLogical Gaps:\n{gaps}"
    if evaluation.logic.alternate_perspectives:
        perspectives = "\n".join(
            f"- {p}" for p in evaluation.logic.alternate_perspectives[:3]
        )
        logic_text += f"\n\nAlternate Perspectives:\n{perspectives}"

    # Attribution chains (compact)
    attribution_text = ""
    if attribution.chains:
        chain_summaries = []
        for chain in attribution.chains[:5]:  # Max 5 chains
            source_label = chain.source.label if chain.source else "No source"
            evidence_count = len(chain.evidence.supporting)
            chain_summaries.append(
                f"Claim: {chain.claim_text[:100]}\n"
                f"  → Source: {source_label}\n"
                f"  → Evidence: {evidence_count} supporting item(s)"
            )
        attribution_text = "\n\nAttribution Chains:\n" + "\n".join(chain_summaries)

    # Claim verification status (if enabled)
    claims_text = ""
    if request.claim_verification_enabled and evaluation.claims:
        claim_statuses = []
        for ec in evaluation.claims[:5]:
            claim_statuses.append(
                f"- {ec.claim_id}: {ec.status.value}"
                + (f" ({ec.verification_note})" if ec.verification_note else "")
            )
        claims_text = "\n\nClaim Verification Status:\n" + "\n".join(claim_statuses)

    # Answer quality notes
    quality_text = ""
    if evaluation.answer_quality:
        aq = evaluation.answer_quality
        quality_parts = []
        if aq.clarity_note:
            quality_parts.append(f"Clarity: {aq.clarity_note}")
        if aq.completeness_note:
            quality_parts.append(f"Completeness: {aq.completeness_note}")
        if aq.actionability_note:
            quality_parts.append(f"Actionability: {aq.actionability_note}")
        if quality_parts:
            quality_text = "\n\nAnswer Quality Notes:\n" + "\n".join(quality_parts)

    # Allowed citation whitelist
    whitelist = _build_citation_whitelist(request, attribution, evaluation)
    whitelist_text = ""
    if whitelist:
        urls = "\n".join(f"- {url}" for url in sorted(whitelist))
        whitelist_text = f"\n\nAllowed Citation URLs (DO NOT cite anything else):\n{urls}"

    packet = {
        "user_query": request.user_query or "N/A",
        "original_response": original_response,
        "user_intent": intent_block,
        "missing_factors": missing_factors_text,
        "logical_gaps": logic_text,
        "attribution": attribution_text,
        "claim_verification": claims_text,
        "answer_quality": quality_text,
        "citation_whitelist": whitelist_text,
    }

    return packet


def _build_system_prompt(
    request: EvaluationRequest,
    whitelist: set[str],
) -> str:
    """Build system prompt for regeneration LLM."""
    expertise_guidance = ""
    if request.answer_quality_intent and request.answer_quality_intent.expertise_level:
        level = request.answer_quality_intent.expertise_level.lower()
        if "beginner" in level or "plain" in level:
            expertise_guidance = "Use simple language, avoid jargon, explain concepts clearly."
        elif "expert" in level or "technical" in level:
            expertise_guidance = "Use concise technical language, assume domain knowledge."
        elif "intermediate" in level:
            expertise_guidance = "Balance clarity with appropriate technical depth."

    source_constraints = ""
    if not request.source_preferences.web:
        source_constraints += "\n- Do NOT use web sources (disabled by user)."
    if not request.source_preferences.research:
        source_constraints += "\n- Do NOT use research sources (disabled by user)."
    if not request.source_preferences.internal:
        source_constraints += "\n- Do NOT rely on internal knowledge (disabled by user)."

    whitelist_warning = ""
    if whitelist:
        whitelist_warning = (
            f"\n\nCRITICAL: You may ONLY cite the {len(whitelist)} URL(s) provided in the whitelist. "
            "DO NOT invent, fabricate, or cite any other sources. "
            "If you need to reference external data but lack citations, use uncertainty language like "
            "'Industry data suggests...' or 'Research indicates...' WITHOUT specific citations."
        )

    return (
        "You are revising an AI answer to match the user's stated intent, expertise level, goal, "
        "constraints, and definition of a good answer.\n\n"
        "INSTRUCTIONS:\n"
        "1. Preserve the user's original query as the primary objective\n"
        "2. Address missing factors where relevant\n"
        "3. Strengthen weak claims with available evidence\n"
        "4. Mark uncertain claims with explicit uncertainty language (e.g., 'likely', 'suggests', 'may')\n"
        "5. Use markdown structure (headings, bullets) for readability\n"
        f"{expertise_guidance}"
        f"{source_constraints}"
        f"{whitelist_warning}"
        "\n\n"
        "CONSTRAINTS:\n"
        "- Do NOT fabricate sources or citations\n"
        "- Do NOT change the core conclusion unless evidence strongly contradicts it\n"
        "- Keep length reasonable (≤1.5× original unless user requested expansion)\n"
        "- Maintain factual accuracy based on provided attribution chains\n"
    )


def _build_user_prompt(packet: dict) -> str:
    """Build user prompt for regeneration LLM."""
    return (
        "Revise the following AI response based on the evaluation findings:\n\n"
        f"### User Query\n{packet['user_query']}\n\n"
        f"### Original Response\n{packet['original_response']}\n\n"
        f"### User Intent\n{packet['user_intent']}\n\n"
        f"{packet['missing_factors']}\n\n"
        f"{packet['logical_gaps']}\n\n"
        f"{packet['attribution']}\n\n"
        f"{packet['claim_verification']}\n\n"
        f"{packet['answer_quality']}\n\n"
        f"{packet['citation_whitelist']}\n\n"
        "### Your Task\n"
        "Produce an improved answer that:\n"
        "1. Addresses the missing factors listed above\n"
        "2. Strengthens claims with available evidence\n"
        "3. Uses appropriate uncertainty language for unverified claims\n"
        "4. Matches the user's expertise level and goals\n"
        "5. Only cites URLs from the whitelist (if any)\n\n"
        "Return ONLY the improved answer in markdown format. Do not include explanations or meta-commentary."
    )


async def _regenerate_with_llm(
    request: EvaluationRequest,
    analysis: AnalysisResult,
    attribution: AttributionResult,
    evaluation: EvaluationResult,
    settings: Settings,
) -> RegenerationResult:
    """Regenerate answer using LLM with evaluation context."""
    from app.adapters.groq_client import create_groq_client

    whitelist = _build_citation_whitelist(request, attribution, evaluation)
    packet = _build_regeneration_packet(request, analysis, attribution, evaluation)

    system_prompt = _build_system_prompt(request, whitelist)
    user_prompt = _build_user_prompt(packet)

    client = create_groq_client(settings)

    response = await client.chat.completions.create(
        model=settings.llm_model_analysis,  # Use analysis model for regeneration
        temperature=0.4,  # Natural prose while staying grounded
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    improved_answer = response.choices[0].message.content or request.ai_response

    # Generate changes summary (rule-based from missing factors)
    changes_summary = _build_changes_summary(evaluation, request)

    # Generate recommended inputs
    recommended_inputs = _build_recommended_inputs(
        request, evaluation, whitelist
    )

    # Determine addressed criteria
    addressed_criteria = _determine_addressed_criteria(request, evaluation)

    return RegenerationResult(
        improved_answer=improved_answer,
        changes_summary=changes_summary,
        recommended_inputs=recommended_inputs,
        addressed_criteria=addressed_criteria,
    )


def _build_changes_summary(
    evaluation: EvaluationResult,
    request: EvaluationRequest,
) -> list[str]:
    """Build changes summary from evaluation findings (rule-based + intent)."""
    changes = []
    seen_keywords: set[str] = set()

    # From missing factors
    for mf in evaluation.missing_factors[:4]:  # Max 4 from factors
        keyword = mf.heading.lower()
        if keyword not in seen_keywords:
            changes.append(f"Added {mf.heading.lower()} discussion")
            seen_keywords.add(keyword)

    # From logical gaps
    if evaluation.logic.logical_gaps:
        changes.append("Addressed logical gaps in reasoning")

    # From claim verification
    if request.claim_verification_enabled and evaluation.claims:
        unverified = [c for c in evaluation.claims if c.status.value != "verified"]
        if unverified:
            changes.append("Qualified unverified claims with uncertainty language")

    # From answer quality intent
    if request.answer_quality_intent:
        intent = request.answer_quality_intent
        if intent.expertise_level:
            changes.append(f"Adjusted tone for {intent.expertise_level} audience")
        if intent.user_goal:
            goal_preview = intent.user_goal[:50]
            changes.append(f"Aligned response with user goal: {goal_preview}")

    # Cap at 8 bullets for UI scannability
    return changes[:MAX_CHANGES_BULLETS]


def _build_recommended_inputs(
    request: EvaluationRequest,
    evaluation: EvaluationResult,
    whitelist: set[str],
) -> list[str]:
    """Build recommended inputs for future improvements."""
    recommendations = []

    # From answer quality intent gaps
    if request.answer_quality_intent:
        intent = request.answer_quality_intent
        if not intent.expertise_level:
            recommendations.append("Specify expertise level (beginner/intermediate/expert)")
        if not intent.user_goal:
            recommendations.append("Define your goal for this evaluation")
        if not intent.good_answer_looks_like:
            recommendations.append("Describe what a good answer would look like")

    # From missing source types
    if evaluation.source_analysis.missing_source_types:
        missing = evaluation.source_analysis.missing_source_types[:2]
        for source_type in missing:
            recommendations.append(
                f"Enable {source_type} sources for additional context"
            )

    # From trust issues
    if evaluation.source_analysis.trust_issues:
        recommendations.append("Provide more authoritative sources (research, company data)")

    # Deduplicate and cap
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            unique_recommendations.append(rec)
        if len(unique_recommendations) >= MAX_RECOMMENDED_INPUTS:
            break

    return unique_recommendations


def _determine_addressed_criteria(
    request: EvaluationRequest,
    evaluation: EvaluationResult,
) -> list[Criteria]:
    """Determine which criteria were addressed in regeneration."""
    addressed = []

    # Missing factors are always addressed
    if evaluation.missing_factors:
        addressed.append(Criteria.MISSING_FACTORS)

    # Answer quality if intent was provided
    if request.answer_quality_intent:
        addressed.append(Criteria.IMPROVE_ANSWER_QUALITY)

    # Logic if there were gaps
    if evaluation.logic.logical_gaps:
        addressed.append(Criteria.LOGIC_REASONING)

    return addressed


def validate_citations(
    text: str,
    allowed_urls: set[str],
) -> list[str]:
    """Validate that all URLs in markdown links are from the whitelist.
    
    Returns list of invalid URLs found in the text.
    """
    # Extract all URLs from markdown links [text](url)
    markdown_urls = re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', text)
    urls_found = [url for _, url in markdown_urls]

    # Extract bare URLs (http:// or https://)
    bare_urls = re.findall(r'https?://[^\s\)]+', text)
    urls_found.extend(bare_urls)

    # Check against whitelist
    invalid_urls = []
    for url in urls_found:
        # Normalize URLs (remove trailing punctuation)
        normalized_url = url.rstrip('.,;:)')
        if normalized_url not in allowed_urls:
            invalid_urls.append(normalized_url)

    return list(set(invalid_urls))  # Deduplicate


def _strip_invalid_citations(text: str, invalid_urls: list[str]) -> str:
    """Remove or replace invalid citations from text."""
    cleaned = text
    for url in invalid_urls:
        # Remove markdown links with invalid URLs
        cleaned = re.sub(
            r'\[([^\]]+)\]\(' + re.escape(url) + r'\)',
            r'\1',  # Keep the link text, remove the URL
            cleaned,
        )
        # Remove bare URLs
        cleaned = cleaned.replace(url, "[citation needed]")

    return cleaned


async def regenerate(
    request: EvaluationRequest,
    analysis: AnalysisResult,
    attribution: AttributionResult,
    evaluation: EvaluationResult,
) -> RegenerationResult | None:
    """Phase 5: Regenerate improved answer based on evaluation findings.
    
    Only runs if:
    - improve_answer_quality is in criteria
    - regenerate is True
    """
    # Check trigger conditions
    if Criteria.IMPROVE_ANSWER_QUALITY not in request.criteria:
        return None

    if not request.regenerate:
        return None

    settings = get_settings()

    # Mock mode: return simple rule-based regeneration
    if settings.mock_mode or not settings.effective_llm_api_key:
        logger.info("Using mock regeneration (MOCK_MODE=true or no API key)")
        return _mock_regeneration(request, evaluation)

    # Live mode: use LLM
    try:
        result = await _regenerate_with_llm(
            request, analysis, attribution, evaluation, settings
        )

        # Validate citations
        whitelist = _build_citation_whitelist(request, attribution, evaluation)
        invalid_urls = validate_citations(result.improved_answer, whitelist)

        if invalid_urls:
            logger.warning(
                "Found %d invalid citation(s) in regenerated answer, stripping...",
                len(invalid_urls),
            )
            result.improved_answer = _strip_invalid_citations(
                result.improved_answer, invalid_urls
            )
            result.changes_summary.insert(
                0,
                f"Removed {len(invalid_urls)} invalid citation(s) not in allowed whitelist",
            )

        return result

    except Exception as exc:
        logger.error("LLM regeneration failed: %s", exc)
        # Fallback to mock regeneration
        return _mock_regeneration(request, evaluation)


def _mock_regeneration(
    request: EvaluationRequest,
    evaluation: EvaluationResult,
) -> RegenerationResult:
    """Mock regeneration for testing/development (no LLM)."""
    improvements = []

    # Address missing factors
    for mf in evaluation.missing_factors[:3]:
        improvements.append(f"\n## {mf.heading}\n{mf.summary}")

    # Add uncertainty for unverified claims
    if request.claim_verification_enabled and evaluation.claims:
        unverified = [c for c in evaluation.claims if c.status.value != "verified"]
        if unverified:
            improvements.append(
                "\n## Note on Uncertainty\n"
                "Some claims in this analysis require additional verification. "
                "Consider the limitations noted above when making decisions."
            )

    # Build improved answer
    original = request.ai_response
    if improvements:
        improved_answer = (
            f"{original}\n\n"
            f"## Improvements Based on Evaluation\n"
            + "\n".join(improvements)
        )
    else:
        improved_answer = original

    # Generate changes summary
    changes_summary = _build_changes_summary(evaluation, request)

    # Generate recommended inputs
    whitelist = set()
    recommended_inputs = _build_recommended_inputs(request, evaluation, whitelist)

    # Addressed criteria
    addressed_criteria = _determine_addressed_criteria(request, evaluation)

    return RegenerationResult(
        improved_answer=improved_answer,
        changes_summary=changes_summary,
        recommended_inputs=recommended_inputs,
        addressed_criteria=addressed_criteria,
    )
