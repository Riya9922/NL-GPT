"""Phase 5 Regeneration Engine tests."""

import pytest

from app.models.analysis import AnalysisResult, Assumption, Claim, ReasoningStep, TextSpan
from app.models.attribution import (
    AttributionMeta,
    AttributionResult,
    ClaimAttributionChain,
    EvidenceBundle,
    EvidenceItem,
    SourceRef,
)
from app.models.enums import ClaimType, Criteria, SourceType
from app.models.evaluation import (
    AnswerQualityNotes,
    EvaluatedClaim,
    EvaluationResult,
    LogicEvaluation,
    MissingFactor,
    SourceAnalysis,
    SourceUsedItem,
)
from app.models.regeneration import RegenerationResult
from app.models.request import (
    AnswerQualityIntent,
    EvaluationRequest,
    SourcePreferences,
    UserContext,
)
from app.services.regeneration import (
    _build_changes_summary,
    _build_recommended_inputs,
    _determine_addressed_criteria,
    regenerate,
    validate_citations,
)


@pytest.fixture
def sample_analysis() -> AnalysisResult:
    return AnalysisResult(
        claims=[
            Claim(
                id="c1",
                text="Users prefer convenience.",
                span=TextSpan(start=0, end=26),
                type=ClaimType.FACTUAL,
            ),
        ],
        assumptions=[
            Assumption(
                id="a1",
                text="Survey represents market.",
                related_claim_ids=["c1"],
            ),
        ],
        reasoning_steps=[
            ReasoningStep(
                id="r1",
                step="Survey shows preference.",
                order=1,
                supports_claim_ids=["c1"],
            ),
        ],
        unsupported_statements=[],
        completeness_notes="Missing sample size.",
    )


@pytest.fixture
def sample_attribution() -> AttributionResult:
    return AttributionResult(
        chains=[
            ClaimAttributionChain(
                claim_id="c1",
                claim_text="Users prefer convenience.",
                source=SourceRef(
                    label="Survey Q7",
                    source_type=SourceType.USER_CONTEXT,
                    url="https://example.com/survey",
                ),
                evidence=EvidenceBundle(
                    supporting=[
                        EvidenceItem(text="73% selected convenience"),
                    ],
                    counter=[
                        EvidenceItem(text="19% selected price"),
                    ],
                ),
                attribution_gap=None,
            ),
        ],
        unlinked_claims=[],
        meta=AttributionMeta(
            sources_respected=["user_context"],
            chains_complete=1,
            chains_with_gaps=0,
        ),
    )


@pytest.fixture
def sample_evaluation() -> EvaluationResult:
    return EvaluationResult(
        claims=[
            EvaluatedClaim(
                claim_id="c1",
                status="verified",
                sources=[],
            ),
        ],
        source_analysis=SourceAnalysis(
            sources_used=[
                SourceUsedItem(
                    source_type=SourceType.USER_CONTEXT,
                    label="Survey Q7",
                    url="https://example.com/survey",
                ),
            ],
            trust_issues=["Limited source diversity"],
            missing_source_types=["research", "company"],
        ),
        logic=LogicEvaluation(
            conclusion="Users prefer convenience.",
            reasoning_path=[],
            logical_gaps=["Missing sample size discussion"],
            alternate_perspectives=["Price may matter to some segments"],
            critique="Reasoning is thin.",
        ),
        missing_factors=[
            MissingFactor(
                heading="Sample Size",
                summary="Survey methodology not provided.",
            ),
            MissingFactor(
                heading="Market Segmentation",
                summary="No breakdown by demographics.",
            ),
        ],
        answer_quality=AnswerQualityNotes(
            clarity_note="Clear but under-supported.",
            completeness_note="Missing methodology details.",
            actionability_note="Need more context.",
            summary="Useful but incomplete.",
        ),
    )


@pytest.fixture
def full_request() -> EvaluationRequest:
    return EvaluationRequest(
        user_query="Should we prioritize convenience?",
        ai_response="Users prefer convenience.",
        criteria=[
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        claim_verification_enabled=True,
        regenerate=True,
        answer_quality_intent=AnswerQualityIntent(
            user_intent="Make a data-driven decision",
            expertise_level="intermediate",
            user_goal="Understand trade-offs",
            constraints_or_expectations="Keep it concise",
            good_answer_looks_like="Clear recommendation with caveats",
        ),
        source_preferences=SourcePreferences(
            memory=False,
            user_context=True,
            web=True,
            research=True,
            company=False,
            internal=False,
        ),
        user_context=UserContext(
            pasted_text="Survey data",
            urls=[],
            file_ids=[],
        ),
    )


@pytest.mark.asyncio
async def test_regeneration_triggers_on_criteria_and_flag(
    full_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
    sample_evaluation: EvaluationResult,
) -> None:
    """Regeneration should run when criteria includes improve_answer_quality and regenerate=True."""
    result = await regenerate(
        full_request, sample_analysis, sample_attribution, sample_evaluation
    )

    assert result is not None
    assert result.improved_answer
    assert len(result.changes_summary) > 0
    assert len(result.addressed_criteria) > 0


@pytest.mark.asyncio
async def test_regeneration_returns_none_when_criteria_missing(
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
    sample_evaluation: EvaluationResult,
) -> None:
    """Regeneration should not run when improve_answer_quality not in criteria."""
    request = EvaluationRequest(
        ai_response="Test",
        criteria=[
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        regenerate=True,
        source_preferences=SourcePreferences(),
    )
    # Remove improve_answer_quality
    request.criteria = [c for c in request.criteria if c != Criteria.IMPROVE_ANSWER_QUALITY]

    result = await regenerate(
        request, sample_analysis, sample_attribution, sample_evaluation
    )

    assert result is None


@pytest.mark.asyncio
async def test_regeneration_returns_none_when_regenerate_false(
    full_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
    sample_evaluation: EvaluationResult,
) -> None:
    """Regeneration should not run when regenerate=False."""
    full_request.regenerate = False

    result = await regenerate(
        full_request, sample_analysis, sample_attribution, sample_evaluation
    )

    assert result is None


def test_changes_summary_from_missing_factors(
    sample_evaluation: EvaluationResult,
    full_request: EvaluationRequest,
) -> None:
    """Changes summary should include bullets for missing factors."""
    changes = _build_changes_summary(sample_evaluation, full_request)

    assert len(changes) > 0
    assert any("sample size" in change.lower() for change in changes)
    assert any("market segmentation" in change.lower() for change in changes)


def test_changes_summary_from_intent(
    sample_evaluation: EvaluationResult,
    full_request: EvaluationRequest,
) -> None:
    """Changes summary should reflect user intent adjustments."""
    changes = _build_changes_summary(sample_evaluation, full_request)

    assert any("intermediate" in change.lower() for change in changes)
    assert any("user goal" in change.lower() for change in changes)


def test_changes_summary_capped_at_8(
    sample_evaluation: EvaluationResult,
    full_request: EvaluationRequest,
) -> None:
    """Changes summary should not exceed 8 bullets."""
    # Add more missing factors
    for i in range(10):
        sample_evaluation.missing_factors.append(
            MissingFactor(
                heading=f"Factor {i}",
                summary=f"Summary {i}",
            )
        )

    changes = _build_changes_summary(sample_evaluation, full_request)
    assert len(changes) <= 8


def test_recommended_inputs_from_missing_sources(
    sample_evaluation: EvaluationResult,
    full_request: EvaluationRequest,
) -> None:
    """Recommended inputs should suggest enabling missing source types."""
    recommendations = _build_recommended_inputs(
        full_request, sample_evaluation, set()
    )

    assert len(recommendations) > 0
    assert any("research" in rec.lower() for rec in recommendations)


def test_recommended_inputs_from_intent_gaps(
    full_request: EvaluationRequest,
    sample_evaluation: EvaluationResult,
) -> None:
    """Recommended inputs should identify missing intent fields."""
    full_request.answer_quality_intent = AnswerQualityIntent(
        user_intent="Test",
        # Missing expertise_level, user_goal, etc.
    )

    recommendations = _build_recommended_inputs(
        full_request, sample_evaluation, set()
    )

    assert any("expertise level" in rec.lower() for rec in recommendations)


def test_recommended_inputs_capped_at_5(
    full_request: EvaluationRequest,
    sample_evaluation: EvaluationResult,
) -> None:
    """Recommended inputs should not exceed 5 items."""
    # Add many missing source types
    sample_evaluation.source_analysis.missing_source_types = [
        "research", "company", "web", "memory", "custom"
    ]
    sample_evaluation.source_analysis.trust_issues = [
        "Issue 1", "Issue 2", "Issue 3"
    ]

    recommendations = _build_recommended_inputs(
        full_request, sample_evaluation, set()
    )

    assert len(recommendations) <= 5


def test_determine_addressed_criteria(
    full_request: EvaluationRequest,
    sample_evaluation: EvaluationResult,
) -> None:
    """Should identify which criteria were addressed."""
    addressed = _determine_addressed_criteria(full_request, sample_evaluation)

    assert Criteria.MISSING_FACTORS in addressed
    assert Criteria.IMPROVE_ANSWER_QUALITY in addressed
    assert Criteria.LOGIC_REASONING in addressed


def test_validate_citations_allows_whitelisted_urls() -> None:
    """Whitelisted URLs should pass validation."""
    text = "Check out [this source](https://example.com/survey)"
    allowed = {"https://example.com/survey"}

    invalid = validate_citations(text, allowed)
    assert len(invalid) == 0


def test_validate_citations_detects_fabricated_urls() -> None:
    """Non-whitelisted URLs should be detected as invalid."""
    text = "According to [fake source](https://fake-domain.com/report)"
    allowed = {"https://example.com/survey"}

    invalid = validate_citations(text, allowed)
    assert len(invalid) == 1
    assert "https://fake-domain.com/report" in invalid


def test_validate_citations_detects_multiple_invalid() -> None:
    """Multiple invalid URLs should all be detected."""
    text = """
    [Source 1](https://fake1.com/a)
    [Source 2](https://fake2.com/b)
    [Valid](https://example.com/survey)
    """
    allowed = {"https://example.com/survey"}

    invalid = validate_citations(text, allowed)
    assert len(invalid) == 2
    assert "https://fake1.com/a" in invalid
    assert "https://fake2.com/b" in invalid


def test_validate_citations_handles_bare_urls() -> None:
    """Bare URLs (not in markdown links) should also be validated."""
    text = "See https://unauthorized.com/data for details"
    allowed = {"https://example.com/survey"}

    invalid = validate_citations(text, allowed)
    assert len(invalid) == 1
    assert "https://unauthorized.com/data" in invalid


@pytest.mark.asyncio
async def test_mock_regeneration_produces_valid_output(
    full_request: EvaluationRequest,
    sample_evaluation: EvaluationResult,
) -> None:
    """Mock regeneration should produce valid RegenerationResult."""
    from app.services.regeneration import _mock_regeneration

    result = _mock_regeneration(full_request, sample_evaluation)

    assert isinstance(result, RegenerationResult)
    assert result.improved_answer
    assert len(result.changes_summary) > 0
    assert len(result.addressed_criteria) > 0


def test_changes_summary_deduplication(
    sample_evaluation: EvaluationResult,
    full_request: EvaluationRequest,
) -> None:
    """Changes summary should not have duplicate bullets."""
    # Add duplicate missing factors
    sample_evaluation.missing_factors.extend([
        MissingFactor(heading="Sample Size", summary="Duplicate 1"),
        MissingFactor(heading="Sample Size", summary="Duplicate 2"),
    ])

    changes = _build_changes_summary(sample_evaluation, full_request)

    # Count how many mention "sample size"
    sample_size_mentions = sum(
        1 for c in changes if "sample size" in c.lower()
    )
    assert sample_size_mentions <= 1
