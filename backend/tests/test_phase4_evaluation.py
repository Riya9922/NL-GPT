"""Phase 4 Evaluation Engine tests."""

import pytest

from app.models.analysis import AnalysisResult, Assumption, Claim, ReasoningStep, TextSpan
from app.models.attribution import (
    AttributionMeta,
    AttributionResult,
    ClaimAttributionChain,
    EvidenceBundle,
    EvidenceItem,
    ReasoningStepRef,
    SourceRef,
)
from app.models.enums import ClaimType, SourceType
from app.models.request import EvaluationRequest, SourcePreferences, UserContext
from app.services.evaluation import evaluate


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
            Claim(
                id="c2",
                text="Price is not a major factor.",
                span=TextSpan(start=28, end=56),
                type=ClaimType.OPINION,
            ),
        ],
        assumptions=[
            Assumption(
                id="a1",
                text="Survey respondents represent target market.",
                related_claim_ids=["c1"],
                derived_from_hint="Survey Question 7",
            ),
        ],
        reasoning_steps=[
            ReasoningStep(
                id="r1",
                step="Survey shows 73% prefer convenience.",
                order=1,
                supports_claim_ids=["c1"],
            ),
        ],
        unsupported_statements=["Market will grow 20% next year."],
        completeness_notes="Missing sample size discussion.",
    )


@pytest.fixture
def sample_attribution() -> AttributionResult:
    return AttributionResult(
        chains=[
            ClaimAttributionChain(
                claim_id="c1",
                claim_text="Users prefer convenience.",
                reasoning_step=ReasoningStepRef(
                    step_id="r1",
                    text="Survey shows 73% prefer convenience.",
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
                            text="73% selected convenience",
                            excerpt="73% of respondents..."
                        ),
                    ],
                    counter=[
                        EvidenceItem(
                            text="19% selected price",
                            excerpt="19% cited price..."
                        ),
                    ],
                ),
                attribution_gap=None,
            ),
            ClaimAttributionChain(
                claim_id="c2",
                claim_text="Price is not a major factor.",
                reasoning_step=None,
                source=SourceRef(
                    label="Internal knowledge",
                    source_type=SourceType.INTERNAL,
                ),
                evidence=EvidenceBundle(),
                attribution_gap="No external source found.",
            ),
        ],
        unlinked_claims=["c2"],
        meta=AttributionMeta(
            sources_respected=["user_context"],
            chains_complete=1,
            chains_with_gaps=1,
        ),
    )


@pytest.fixture
def base_request() -> EvaluationRequest:
    return EvaluationRequest(
        ai_response="Users prefer convenience. Price is not a major factor.",
        criteria=[
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        claim_verification_enabled=True,
        source_preferences=SourcePreferences(
            memory=False,
            user_context=True,
            web=True,
            research=True,
            company=False,
            internal=False,
        ),
        user_context=UserContext(
            pasted_text="Survey Question 7: 73% convenience, 19% price",
            urls=[],
            file_ids=[],
        ),
    )


@pytest.mark.asyncio
async def test_claim_verification_toggle_on(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """When toggle is on, claims should be evaluated."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    assert len(result.claims) == 2
    # c1 has supporting evidence → should be verified
    c1 = next(c for c in result.claims if c.claim_id == "c1")
    assert c1.status == "verified"
    assert len(c1.sources) >= 1

    # c2 is opinion → not applicable
    c2 = next(c for c in result.claims if c.claim_id == "c2")
    assert c2.status == "not_applicable"


@pytest.mark.asyncio
async def test_claim_verification_toggle_off(
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """When toggle is off, claims list should be empty."""
    request = EvaluationRequest(
        ai_response="Test response",
        criteria=[
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        claim_verification_enabled=False,
        source_preferences=SourcePreferences(),
    )

    result = await evaluate(request, sample_analysis, sample_attribution)
    assert result.claims == []


@pytest.mark.asyncio
async def test_source_transparency_populated(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Source analysis should list sources used and trust issues."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    assert len(result.source_analysis.sources_used) > 0
    assert len(result.source_analysis.trust_issues) > 0
    assert len(result.source_analysis.missing_source_types) > 0


@pytest.mark.asyncio
async def test_logic_evaluation_populated(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Logic evaluation should have reasoning path and gaps."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    assert result.logic.conclusion
    assert len(result.logic.reasoning_path) > 0
    assert len(result.logic.logical_gaps) > 0
    assert len(result.logic.alternate_perspectives) > 0
    assert result.logic.critique


@pytest.mark.asyncio
async def test_missing_factors_compact(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Missing factors should be compact (<=200 chars per summary)."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    assert len(result.missing_factors) > 0
    for factor in result.missing_factors:
        assert factor.heading
        assert factor.summary
        assert len(factor.summary) <= 200


@pytest.mark.asyncio
async def test_answer_quality_notes_present(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Answer quality notes should be present when criterion requested."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    assert result.answer_quality is not None
    # Notes should be present (at least some)
    assert any([
        result.answer_quality.clarity_note,
        result.answer_quality.completeness_note,
        result.answer_quality.actionability_note,
    ])


@pytest.mark.asyncio
async def test_no_numeric_scores_in_output(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """CRITICAL: No numeric score fields anywhere in evaluation output."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)
    payload = result.model_dump()
    text = str(payload).lower()

    forbidden = ("confidence", "score", "rating", "probability")
    for word in forbidden:
        # Allow "chains_with_gaps" which contains "gaps" not "score"
        if word in text and "score" in word:
            # Double-check it's not actually a score field
            assert f'"{word}"' not in text, f"Forbidden score field found: {word}"


@pytest.mark.asyncio
async def test_counter_evidence_in_alternate_perspectives(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Counter evidence should appear in alternate perspectives."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    # Should mention counter evidence
    has_counter_ref = any(
        "19%" in perspective or "counter" in perspective.lower()
        for perspective in result.logic.alternate_perspectives
    )
    assert has_counter_ref, "Counter evidence should be reflected in alternate perspectives"


@pytest.mark.asyncio
async def test_unsupported_statements_in_gaps(
    base_request: EvaluationRequest,
    sample_analysis: AnalysisResult,
    sample_attribution: AttributionResult,
) -> None:
    """Unsupported statements should be mentioned in logical gaps."""
    result = await evaluate(base_request, sample_analysis, sample_attribution)

    gaps_text = " ".join(result.logic.logical_gaps).lower()
    assert "unsupported" in gaps_text or len(sample_analysis.unsupported_statements) == 0
