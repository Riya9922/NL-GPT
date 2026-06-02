"""Phase 4 — Evaluation Engine.

Produces qualitative outputs for five evaluation dimensions:
1. Claim verification (toggle-gated)
2. Source transparency
3. Logic & reasoning
4. Missing factors
5. Improve answer quality (narrative notes)

NO scoring anywhere — no confidence, percentages, or 1-5 scales.
"""

from __future__ import annotations

import json
import logging

from app.config import Settings, get_settings
from app.models.analysis import AnalysisResult
from app.models.attribution import AttributionResult, ClaimAttributionChain
from app.models.enums import (
    ClaimType,
    ClaimVerificationStatus,
    Criteria,
    SourceType,
)
from app.models.evaluation import (
    AnswerQualityNotes,
    EvaluatedClaim,
    EvaluationResult,
    EvidenceLink,
    LogicEvaluation,
    MissingFactor,
    ReasoningPathStep,
    SourceAnalysis,
    SourceUsedItem,
    VerificationSource,
)
from app.models.request import AnswerQualityIntent, EvaluationRequest

logger = logging.getLogger(__name__)


def _evaluate_claims_toggle_off() -> list[EvaluatedClaim]:
    """When claim verification is disabled, return empty list."""
    return []


def _evaluate_claim_from_chain(
    chain: ClaimAttributionChain,
    claim_type: ClaimType,
    internal_allowed: bool,
) -> EvaluatedClaim:
    """Evaluate a single claim using its attribution chain."""
    # Opinion claims are not applicable for verification
    if claim_type == ClaimType.OPINION:
        return EvaluatedClaim(
            claim_id=chain.claim_id,
            status=ClaimVerificationStatus.NOT_APPLICABLE,
            sources=[],
            verification_note="Opinion-based claim; verification not applicable.",
        )

    # Check if we have supporting evidence from allowed sources
    has_supporting = len(chain.evidence.supporting) > 0
    has_counter = len(chain.evidence.counter) > 0
    source_type = chain.source.source_type if chain.source else None

    # Internal knowledge alone cannot verify
    if source_type == SourceType.INTERNAL and not internal_allowed:
        return EvaluatedClaim(
            claim_id=chain.claim_id,
            status=ClaimVerificationStatus.NEEDS_VERIFICATION,
            sources=[],
            verification_note="Claim relies on internal knowledge; external verification needed.",
        )

    # Contradicting evidence present
    if has_counter and not has_supporting:
        return EvaluatedClaim(
            claim_id=chain.claim_id,
            status=ClaimVerificationStatus.UNSUPPORTED,
            sources=[],
            verification_note="Available evidence contradicts this claim.",
        )

    # Strong support from allowed sources - ALWAYS verify if we have evidence
    # This takes priority over attribution gaps
    if has_supporting and chain.source:
        sources = [
            VerificationSource(
                title=chain.source.label,
                url=chain.source.url,
                source_type=chain.source.source_type or SourceType.USER_CONTEXT,
                snippet=item.text,
            )
            for item in chain.evidence.supporting[:3]  # Max 3 sources
        ]
        return EvaluatedClaim(
            claim_id=chain.claim_id,
            status=ClaimVerificationStatus.VERIFIED,
            sources=sources,
            verification_note=None,
        )

    # Partial support or gaps (only if no strong support)
    if has_supporting and chain.attribution_gap:
        sources = []
        if chain.source:
            sources.append(
                VerificationSource(
                    title=chain.source.label,
                    url=chain.source.url,
                    source_type=chain.source.source_type or SourceType.USER_CONTEXT,
                    snippet=chain.evidence.supporting[0].text if chain.evidence.supporting else None,
                )
            )
        # If we have evidence from web sources, still mark as VERIFIED
        if source_type == SourceType.WEB or source_type == SourceType.RESEARCH:
            return EvaluatedClaim(
                claim_id=chain.claim_id,
                status=ClaimVerificationStatus.VERIFIED,
                sources=sources,
                verification_note=None,
            )
        return EvaluatedClaim(
            claim_id=chain.claim_id,
            status=ClaimVerificationStatus.NEEDS_VERIFICATION,
            sources=sources,
            verification_note=f"Partial support found, but: {chain.attribution_gap}",
        )

    # Default: needs verification
    return EvaluatedClaim(
        claim_id=chain.claim_id,
        status=ClaimVerificationStatus.NEEDS_VERIFICATION,
        sources=[],
        verification_note="No sufficient evidence found in provided sources.",
    )


def _build_claim_verification(
    request: EvaluationRequest,
    analysis: AnalysisResult,
    attribution: AttributionResult,
) -> list[EvaluatedClaim]:
    """Phase 4.2: Claim verification module (toggle-gated)."""
    if not request.claim_verification_enabled:
        return _evaluate_claims_toggle_off()

    internal_allowed = request.source_preferences.internal

    # Build chain lookup
    chain_map = {chain.claim_id: chain for chain in attribution.chains}

    # Build claim type lookup
    claim_type_map = {claim.id: claim.type for claim in analysis.claims}

    evaluated = []
    for claim in analysis.claims:
        chain = chain_map.get(claim.id)
        if chain is None:
            # No attribution chain found
            evaluated.append(
                EvaluatedClaim(
                    claim_id=claim.id,
                    status=ClaimVerificationStatus.NEEDS_VERIFICATION,
                    sources=[],
                    verification_note="No attribution chain available for this claim.",
                )
            )
        else:
            evaluated.append(
                _evaluate_claim_from_chain(chain, claim.type, internal_allowed)
            )

    return evaluated


def _build_source_transparency(
    request: EvaluationRequest,
    attribution: AttributionResult,
) -> SourceAnalysis:
    """Phase 4.3: Source transparency module."""
    # Collect unique sources used
    sources_used_map: dict[str, SourceUsedItem] = {}
    for chain in attribution.chains:
        if chain.source:
            key = f"{chain.source.source_type.value}:{chain.source.label}"
            if key not in sources_used_map:
                sources_used_map[key] = SourceUsedItem(
                    source_type=chain.source.source_type or SourceType.USER_CONTEXT,
                    label=chain.source.label,
                    url=chain.source.url,
                )

    sources_used = list(sources_used_map.values())

    # Identify trust issues (narrative, no scores)
    trust_issues = []
    source_types_used = {s.source_type for s in sources_used}

    if SourceType.WEB in source_types_used and not any(
        st in source_types_used for st in [SourceType.RESEARCH, SourceType.COMPANY]
    ):
        trust_issues.append("Only web sources cited; no peer-reviewed or company data.")

    if SourceType.INTERNAL in source_types_used:
        trust_issues.append(
            "Some claims rely on internal knowledge without external citations."
        )

    chains_with_gaps = [c for c in attribution.chains if c.attribution_gap]
    if chains_with_gaps:
        trust_issues.append(
            f"{len(chains_with_gaps)} claim(s) have attribution gaps in source linking."
        )

    if not sources_used:
        trust_issues.append("No sources identified in the response.")

    # Identify missing source types that would help
    allowed_types = {
        st
        for st, enabled in {
            SourceType.MEMORY: request.source_preferences.memory,
            SourceType.USER_CONTEXT: request.source_preferences.user_context,
            SourceType.WEB: request.source_preferences.web,
            SourceType.RESEARCH: request.source_preferences.research,
            SourceType.COMPANY: request.source_preferences.company,
        }.items()
        if enabled
    }

    missing_source_types = [
        st.value
        for st in [SourceType.RESEARCH, SourceType.COMPANY, SourceType.WEB]
        if st in allowed_types and st not in source_types_used
    ]

    return SourceAnalysis(
        sources_used=sources_used,
        trust_issues=trust_issues,
        missing_source_types=missing_source_types,
    )


def _build_logic_evaluation(
    analysis: AnalysisResult,
    attribution: AttributionResult,
) -> LogicEvaluation:
    """Phase 4.4: Logic & reasoning module."""
    # Extract conclusion from first claim or reasoning step
    conclusion = ""
    if analysis.claims:
        conclusion = analysis.claims[0].text

    # Build reasoning path with evidence links from attribution
    reasoning_path = []
    chain_map = {chain.claim_id: chain for chain in attribution.chains}

    for step in analysis.reasoning_steps[:4]:  # Max 4 steps
        # Find evidence links from attribution chains that support this step
        evidence_links = []
        for claim_id in step.supports_claim_ids:
            chain = chain_map.get(claim_id)
            if chain and chain.source:
                evidence_links.append(
                    EvidenceLink(
                        label=chain.source.label,
                        url=chain.source.url,
                    )
                )

        # Build expandable detail from attribution evidence
        expandable_detail = None
        supporting_claims = [chain_map.get(cid) for cid in step.supports_claim_ids]
        evidence_texts = []
        for chain in supporting_claims:
            if chain and chain.evidence.supporting:
                evidence_texts.extend(
                    [item.text for item in chain.evidence.supporting[:2]]
                )
        if evidence_texts:
            expandable_detail = "Evidence Used: " + "; ".join(evidence_texts[:3])

        reasoning_path.append(
            ReasoningPathStep(
                step_id=step.id,
                text=step.step,
                evidence_links=evidence_links,
                expandable_detail=expandable_detail,
            )
        )

    # Identify logical gaps
    logical_gaps = []
    if analysis.completeness_notes:
        logical_gaps.append(analysis.completeness_notes)

    unsupported_from_analysis = analysis.unsupported_statements
    if unsupported_from_analysis:
        logical_gaps.append(
            f"Unsupported statements detected: {len(unsupported_from_analysis)}"
        )

    chains_with_gaps = [c for c in attribution.chains if c.attribution_gap]
    if chains_with_gaps:
        gap_details = "; ".join(
            [f"{c.claim_id}: {c.attribution_gap}" for c in chains_with_gaps[:2]]
        )
        logical_gaps.append(f"Attribution gaps: {gap_details}")

    # Generate alternate perspectives
    alternate_perspectives = []
    claims_with_counter = [
        c for c in attribution.chains if c.evidence.counter
    ]
    if claims_with_counter:
        chain = claims_with_counter[0]
        counter_text = chain.evidence.counter[0].text if chain.evidence.counter else ""
        if counter_text:
            alternate_perspectives.append(
                f"Counter-evidence suggests: {counter_text}"
            )

    if analysis.assumptions:
        alternate_perspectives.append(
            f"Key assumption to validate: {analysis.assumptions[0].text}"
        )

    # Add generic alternates if we have fewer than 2
    if len(alternate_perspectives) < 2:
        alternate_perspectives.append(
            "Alternative interpretations may exist based on different source priorities."
        )

    # Build critique
    critique_parts = []
    if not reasoning_path:
        critique_parts.append("No explicit reasoning steps identified.")
    if logical_gaps:
        critique_parts.append(
            f"Reasoning has {len(logical_gaps)} gap(s) that weaken the conclusion."
        )
    if not critique_parts:
        critique_parts.append(
            "Reasoning chain is present but would benefit from additional source diversity."
        )

    critique = " ".join(critique_parts)

    return LogicEvaluation(
        conclusion=conclusion,
        reasoning_path=reasoning_path,
        logical_gaps=logical_gaps,
        alternate_perspectives=alternate_perspectives[:4],  # Max 4
        critique=critique,
    )


def _build_missing_factors(
    analysis: AnalysisResult,
    attribution: AttributionResult,
    request: EvaluationRequest,
) -> list[MissingFactor]:
    """Phase 4.5: Missing factors module (compact gap items, ~200 chars max)."""
    missing = []

    # Check for missing source types
    source_analysis = _build_source_transparency(request, attribution)
    for missing_type in source_analysis.missing_source_types:
        type_labels = {
            "research": "External Research",
            "company": "Company Data",
            "web": "Web Sources",
        }
        label = type_labels.get(missing_type, missing_type)
        missing.append(
            MissingFactor(
                heading=f"{label} Sources",
                summary=f"No {missing_type} sources were used to validate claims.",
            )
        )

    # Check for attribution gaps
    gaps = [c for c in attribution.chains if c.attribution_gap]
    if gaps:
        missing.append(
            MissingFactor(
                heading="Source Attribution",
                summary=f"{len(gaps)} claim(s) lack complete source attribution chains.",
            )
        )

    # Check for unsupported statements
    if analysis.unsupported_statements:
        missing.append(
            MissingFactor(
                heading="Unsupported Claims",
                summary=f"{len(analysis.unsupported_statements)} statement(s) have no clear support in provided sources.",
            )
        )

    # Check for assumptions that need validation
    if analysis.assumptions:
        missing.append(
            MissingFactor(
                heading="Unvalidated Assumptions",
                summary=f"{len(analysis.assumptions)} assumption(s) underlie the reasoning but are not independently verified.",
            )
        )

    # Check completeness notes for additional gaps
    if analysis.completeness_notes:
        missing.append(
            MissingFactor(
                heading="Coverage Gaps",
                summary=analysis.completeness_notes[:200],
            )
        )

    # Cap at reasonable number for UI density
    return missing[:6]


def _build_answer_quality_notes(
    analysis: AnalysisResult,
    attribution: AttributionResult,
    intent: AnswerQualityIntent | None,
) -> AnswerQualityNotes | None:
    """Phase 4.6: Improve answer quality (narrative only, no scores)."""
    # Calculate qualitative metrics
    total_claims = len(attribution.chains)
    complete_chains = len([c for c in attribution.chains if not c.attribution_gap])
    has_counter_evidence = any(c.evidence.counter for c in attribution.chains)

    # Clarity note
    clarity_note = None
    if total_claims > 0:
        if complete_chains == total_claims:
            clarity_note = "Claims are clearly stated and fully supported by sources."
        elif complete_chains > 0:
            clarity_note = f"Claims are stated, but {total_claims - complete_chains} lack complete source support."
        else:
            clarity_note = "Claims are present but lack sufficient source attribution."

    # Completeness note
    completeness_note = None
    missing_count = len(analysis.unsupported_statements)
    if missing_count > 0:
        completeness_note = (
            f"Response has {missing_count} unsupported statement(s) and may be missing key context."
        )
    elif analysis.completeness_notes:
        completeness_note = analysis.completeness_notes[:150]

    # Actionability note
    actionability_note = None
    if has_counter_evidence:
        actionability_note = (
            "Decision should weigh both supporting and counter-evidence presented."
        )
    elif complete_chains < total_claims and total_claims > 0:
        actionability_note = (
            "Recommendation may be premature; fill attribution gaps before deciding."
        )

    # Summary
    summary = None
    if clarity_note and completeness_note:
        summary = f"{' '.join(clarity_note.split()[:10])} {' '.join(completeness_note.split()[:10])}."
    elif clarity_note:
        summary = clarity_note

    # Only return if we have meaningful notes
    if not any([clarity_note, completeness_note, actionability_note, summary]):
        return None

    return AnswerQualityNotes(
        clarity_note=clarity_note,
        completeness_note=completeness_note,
        actionability_note=actionability_note,
        summary=summary,
    )


async def evaluate(
    request: EvaluationRequest,
    analysis: AnalysisResult,
    attribution: AttributionResult,
) -> EvaluationResult:
    """Phase 4: Produce qualitative evaluation across all dimensions.

    No scoring anywhere — only narrative and structured qualitative outputs.
    """
    settings = get_settings()

    # Use mock evaluation data when in mock mode
    if settings.mock_mode:
        from app.fixtures.mock_evaluate import build_mock_evaluation
        return build_mock_evaluation(request.claim_verification_enabled)

    # 1. Claim verification (toggle-gated)
    claims = _build_claim_verification(request, analysis, attribution)

    # 2. Source transparency
    source_analysis = _build_source_transparency(request, attribution)

    # 3. Logic & reasoning
    logic = _build_logic_evaluation(analysis, attribution)

    # 4. Missing factors
    missing_factors = _build_missing_factors(analysis, attribution, request)

    # 5. Answer quality notes (if criterion requested)
    answer_quality = None
    if Criteria.IMPROVE_ANSWER_QUALITY in request.criteria:
        answer_quality = _build_answer_quality_notes(
            analysis, attribution, request.answer_quality_intent
        )

    return EvaluationResult(
        claims=claims,
        source_analysis=source_analysis,
        logic=logic,
        missing_factors=missing_factors,
        answer_quality=answer_quality,
    )
