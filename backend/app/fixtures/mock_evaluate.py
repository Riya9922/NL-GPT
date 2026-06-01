"""SNITCH / Bangalore mock payload for Phase 1 contract testing."""

from app.models.analysis import (
    AnalysisResult,
    Assumption,
    Claim,
    ReasoningStep,
    TextSpan,
)
from app.models.attribution import (
    AssumptionAttribution,
    AttributionMeta,
    AttributionResult,
    ClaimAttributionChain,
    EvidenceBundle,
    EvidenceItem,
    ReasoningStepRef,
    SourceRef,
)
from app.models.enums import (
    ALL_CRITERIA,
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
from app.models.regeneration import RegenerationResult
from app.models.request import AnswerQualityIntent, EvaluationRequest


def build_mock_analysis() -> AnalysisResult:
    """Golden analysis fixture aligned with Phase 3.5 convenience/survey example."""
    return AnalysisResult(
        claims=[
            Claim(
                id="c1",
                text="Users prefer convenience.",
                span=TextSpan(start=0, end=26),
                type=ClaimType.FACTUAL,
            ),
            Claim(
                id="c2",
                text="Price sensitivity is secondary to ease of access.",
                span=TextSpan(start=28, end=78),
                type=ClaimType.FACTUAL,
            ),
        ],
        assumptions=[
            Assumption(
                id="a1",
                text="Users prefer convenience.",
                related_claim_ids=["c1"],
                derived_from_hint="Survey Question 7",
            ),
            Assumption(
                id="a2",
                text="Survey respondents represent the broader target market.",
                related_claim_ids=["c1", "c2"],
                derived_from_hint="Survey methodology",
            ),
        ],
        reasoning_steps=[
            ReasoningStep(
                id="r1",
                step="Survey results show a majority favor convenience over price.",
                order=1,
                supports_claim_ids=["c1"],
            ),
            ReasoningStep(
                id="r2",
                step="Demand is driven by ease of access rather than price sensitivity.",
                order=2,
                supports_claim_ids=["c1", "c2"],
            ),
        ],
        unsupported_statements=[],
        completeness_notes=(
            "Answer cites survey data but does not discuss sample size or "
            "demographic breakdown of respondents."
        ),
    )


def build_mock_attribution() -> AttributionResult:
    """Golden attribution fixture for Survey Q7 / convenience example (Phase 3.5)."""
    return AttributionResult(
        chains=[
            ClaimAttributionChain(
                claim_id="c1",
                claim_text="Users prefer convenience.",
                reasoning_step=ReasoningStepRef(
                    step_id="r1",
                    text="Survey results show a majority favor convenience over price.",
                ),
                source=SourceRef(
                    source_id="s1",
                    label="Survey Question 7",
                    source_type=SourceType.USER_CONTEXT,
                    citation_index=7,
                ),
                evidence=EvidenceBundle(
                    supporting=[
                        EvidenceItem(
                            text="73% of respondents selected convenience",
                            excerpt="When asked to choose between convenience and price, 73% of survey respondents indicated convenience as their primary factor."
                        ),
                    ],
                    counter=[
                        EvidenceItem(
                            text="19% selected price",
                            excerpt="Only 19% of respondents cited price as the deciding factor."
                        ),
                    ],
                ),
                assumption=AssumptionAttribution(
                    text="Users prefer convenience.",
                    derived_from="Survey Question 7",
                    supporting_evidence="73% respondents selected convenience",
                    counter_evidence="19% selected price",
                ),
                attribution_gap=None,
            ),
            ClaimAttributionChain(
                claim_id="c2",
                claim_text="Price sensitivity is secondary to ease of access.",
                reasoning_step=ReasoningStepRef(
                    step_id="r2",
                    text="Demand is driven by ease of access rather than price sensitivity.",
                ),
                source=SourceRef(
                    source_id="s1",
                    label="Survey Question 7",
                    source_type=SourceType.USER_CONTEXT,
                    citation_index=7,
                ),
                evidence=EvidenceBundle(
                    supporting=[
                        EvidenceItem(
                            text="73% prioritized convenience over price",
                            excerpt="Survey data shows convenience outweighs price considerations for the majority."
                        ),
                    ],
                    counter=[
                        EvidenceItem(
                            text="19% selected price as primary factor",
                            excerpt="A minority segment remains price-sensitive."
                        ),
                    ],
                ),
                assumption=AssumptionAttribution(
                    text="Survey respondents represent the broader target market.",
                    derived_from="Survey methodology",
                    supporting_evidence="73% prioritized convenience over price",
                    counter_evidence="19% selected price as primary factor",
                ),
                attribution_gap=None,
            ),
        ],
        unlinked_claims=[],
        meta=AttributionMeta(
            sources_respected=["user_context", "research"],
            chains_complete=2,
            chains_with_gaps=0,
        ),
    )


def build_mock_evaluation(
    claim_verification_enabled: bool,
) -> EvaluationResult:
    """Mock evaluation aligned with Phase 3.5 convenience/survey example."""
    claims: list[EvaluatedClaim] = []
    if claim_verification_enabled:
        claims = [
            EvaluatedClaim(
                claim_id="c1",
                status=ClaimVerificationStatus.VERIFIED,
                sources=[
                    VerificationSource(
                        title="Consumer Behavior Survey 2024",
                        url="https://example.com/survey-2024",
                        source_type=SourceType.RESEARCH,
                        snippet="73% of consumers prioritize convenience over price when making purchasing decisions.",
                    ),
                    VerificationSource(
                        title="Retail Market Analysis Report",
                        url="https://example.com/retail-report",
                        source_type=SourceType.RESEARCH,
                        snippet="Convenience-driven shopping behavior has increased by 45% since 2020.",
                    ),
                    VerificationSource(
                        title="Industry Trends: Convenience Economy",
                        url=None,
                        source_type=SourceType.RESEARCH,
                        snippet="Market research confirms convenience is the primary decision factor for modern consumers.",
                    ),
                ],
                verification_note=None,
            ),
            EvaluatedClaim(
                claim_id="c2",
                status=ClaimVerificationStatus.NEEDS_VERIFICATION,
                sources=[],
                verification_note="Price sensitivity varies by demographic and region; requires additional market-specific research.",
            ),
        ]

    return EvaluationResult(
        claims=claims,
        source_analysis=SourceAnalysis(
            sources_used=[
                SourceUsedItem(
                    source_type=SourceType.USER_CONTEXT,
                    label="Survey Question 7 - convenience vs price preference",
                ),
                SourceUsedItem(
                    source_type=SourceType.INTERNAL,
                    label="General reasoning about consumer preferences",
                ),
            ],
            trust_issues=["Survey sample size and demographics not disclosed."],
            missing_source_types=["research", "company"],
        ),
        logic=LogicEvaluation(
            conclusion="Users prefer convenience over price based on survey data.",
            reasoning_path=[
                ReasoningPathStep(
                    step_id="r1",
                    text="Survey results show a majority favor convenience over price.",
                    evidence_links=[
                        EvidenceLink(label="Survey Question 7", url=None),
                    ],
                    expandable_detail="Evidence Used: 73% convenience vs 19% price preference.",
                ),
                ReasoningPathStep(
                    step_id="r2",
                    text="Demand is driven by ease of access rather than price sensitivity.",
                    evidence_links=[
                        EvidenceLink(label="Survey Question 7", url=None),
                    ],
                ),
            ],
            logical_gaps=[
                "Conclusion assumes survey respondents represent the broader target market without validation.",
                "Survey sample size and demographic breakdown not disclosed, limiting generalizability.",
                "Price sensitivity may still be a factor for specific segments not captured in the survey.",
                "External market conditions and competitor presence not considered in the analysis.",
            ],
            alternate_perspectives=[
                "Price-sensitive segment (19%) may represent a significant market opportunity.",
                "Convenience preference may vary by demographic or geographic segment.",
            ],
            critique=(
                "The reasoning chain is grounded in survey data but lacks external validation "
                "and does not address potential sampling bias or demographic limitations."
            ),
        ),
        missing_factors=[
            MissingFactor(
                heading="Sample Size and Demographics",
                summary="Survey methodology and respondent breakdown not provided.",
            ),
            MissingFactor(
                heading="Market Segmentation",
                summary="No analysis of how preferences vary across user segments.",
            ),
            MissingFactor(
                heading="External Market Research",
                summary="No third-party data to validate survey findings.",
            ),
        ],
        answer_quality=AnswerQualityNotes(
            clarity_note="Claim is clear and directly supported by survey data.",
            completeness_note="Misses methodology details and external validation.",
            actionability_note="Decision requires understanding of survey representativeness.",
            summary="Directionally useful but not fully decision-ready without context.",
        ),
    )


def build_mock_regeneration(intent: AnswerQualityIntent | None) -> RegenerationResult:
    expertise = (intent.expertise_level if intent else None) or "intermediate"
    goal = (intent.user_goal if intent else None) or "a clear go/no-go recommendation"

    return RegenerationResult(
        improved_answer=(
            f"## Executive summary\n\n"
            f"Bangalore may be attractive for SNITCH, but the original answer does not yet "
            f"support a confident expansion decision. This revision is tailored for "
            f"**{expertise}** readers who need **{goal}**.\n\n"
            f"## What we know\n"
            f"- Brand awareness signals exist (stores, social engagement).\n"
            f"- Demand is suggested but not quantified with third-party data.\n\n"
            f"## Gaps to close before deciding\n"
            f"- Competitor footprint and pricing in target micro-markets.\n"
            f"- Rent, unit economics, and payback for a new store.\n"
            f"- Cannibalization impact on existing Bangalore locations.\n\n"
            f"## Recommendation\n"
            f"Treat Bangalore as a **conditional yes**: proceed only after filling the gaps above."
        ),
        changes_summary=[
            "Added competitor, economics, cannibalization, and saturation sections.",
            "Qualified the market-strength claim where evidence is thin.",
            "Structured output for board-style decision making.",
        ],
        recommended_inputs=[],
        addressed_criteria=[
            Criteria.MISSING_FACTORS,
            Criteria.IMPROVE_ANSWER_QUALITY,
        ],
    )


def build_mock_payload(req: EvaluationRequest) -> tuple[
    AnalysisResult,
    AttributionResult,
    EvaluationResult,
    RegenerationResult | None,
]:
    analysis = build_mock_analysis()
    attribution = build_mock_attribution()
    evaluation = build_mock_evaluation(req.claim_verification_enabled)
    regeneration = None
    if Criteria.IMPROVE_ANSWER_QUALITY in req.criteria and req.regenerate:
        regeneration = build_mock_regeneration(req.answer_quality_intent)
    return analysis, attribution, evaluation, regeneration
