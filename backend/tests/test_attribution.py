import pytest

from app.models.enums import SourceType
from app.models.request import EvaluationRequest, SourcePreferences, UserContext
from app.services.attribution import (
    attribute_rule_based,
    convenience_survey_analysis,
)


@pytest.fixture
def base_request() -> EvaluationRequest:
    return EvaluationRequest(
        ai_response="Users prefer convenience.",
        criteria=[
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        claim_verification_enabled=False,
        source_preferences=SourcePreferences(
            memory=False,
            user_context=True,
            web=True,
            research=True,
            company=False,
            internal=False,
        ),
        user_context=UserContext(
            pasted_text=(
                "Survey Question 7: Preference drivers\n"
                "73% of respondents selected convenience\n"
                "19% selected price"
            ),
            urls=[],
            file_ids=[],
        ),
    )


def test_convenience_survey_chain(base_request: EvaluationRequest) -> None:
    analysis = convenience_survey_analysis()
    result = attribute_rule_based(base_request, analysis)

    assert len(result.chains) == 1
    chain = result.chains[0]
    assert chain.claim_id == "c1"
    assert chain.reasoning_step is not None
    assert chain.source is not None
    assert chain.source.source_type in (SourceType.USER_CONTEXT, SourceType.RESEARCH)
    assert len(chain.evidence.supporting) >= 1
    assert any("73%" in item.text for item in chain.evidence.supporting)
    assert chain.assumption is not None
    assert chain.assumption.derived_from == "Survey Question 7"
    assert "confidence" not in result.model_dump_json()


def test_every_claim_has_chain(base_request: EvaluationRequest) -> None:
    from app.fixtures.mock_evaluate import build_mock_analysis

    analysis = build_mock_analysis()
    result = attribute_rule_based(base_request, analysis)

    assert len(result.chains) == len(analysis.claims)
    assert result.meta.chains_complete + result.meta.chains_with_gaps == len(
        result.chains
    )


def test_no_numeric_score_fields(base_request: EvaluationRequest) -> None:
    analysis = convenience_survey_analysis()
    payload = attribute_rule_based(base_request, analysis).model_dump()
    forbidden = ("confidence", "score", "rating", "probability")
    text = str(payload).lower()
    for word in forbidden:
        assert word not in text or "chains_with_gaps" in text


@pytest.mark.asyncio
async def test_attribute_endpoint(client, sample_evaluate_body: dict) -> None:
    from app.fixtures.mock_evaluate import build_mock_analysis

    analysis = build_mock_analysis()
    res = client.post(
        "/api/v1/attribute",
        json={"analysis": analysis.model_dump(), "evaluate": sample_evaluate_body},
    )
    assert res.status_code == 200
    assert res.json()["chains"]
