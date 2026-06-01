import json
from pathlib import Path

import pytest

from app.models.request import EvaluationRequest
from app.orchestrator import run_evaluation

FORBIDDEN_SCORE_KEYS = {
    "confidence",
    "score",
    "severity",
    "clarity",
    "completeness",
    "actionability",
    "rating",
}


def _collect_keys(obj: object, keys: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORBIDDEN_SCORE_KEYS and isinstance(value, (int, float)):
                keys.add(key)
            _collect_keys(value, keys)
    elif isinstance(obj, list):
        for item in obj:
            _collect_keys(item, keys)


@pytest.mark.asyncio
async def test_orchestrator_returns_complete_contract(sample_evaluate_body: dict) -> None:
    req = EvaluationRequest.model_validate(sample_evaluate_body)
    response = await run_evaluation(req)

    assert response.status.value == "completed"
    assert response.analysis.claims
    assert response.attribution.chains is not None
    assert len(response.evaluation.missing_factors) >= 1
    assert all(len(mf.summary) <= 200 for mf in response.evaluation.missing_factors)
    assert response.regeneration is not None
    assert response.meta.dimensions
    assert len(response.meta.dimensions) == 5


@pytest.mark.asyncio
async def test_claim_verification_off_empty_claims(sample_evaluate_body: dict) -> None:
    sample_evaluate_body["claim_verification_enabled"] = False
    req = EvaluationRequest.model_validate(sample_evaluate_body)
    response = await run_evaluation(req)
    assert response.evaluation.claims == []


@pytest.mark.asyncio
async def test_claim_verification_on_populates_claims(sample_evaluate_body: dict) -> None:
    sample_evaluate_body["claim_verification_enabled"] = True
    req = EvaluationRequest.model_validate(sample_evaluate_body)
    response = await run_evaluation(req)
    assert len(response.evaluation.claims) >= 1


def test_health(client) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_evaluate_endpoint(client, sample_evaluate_body: dict) -> None:
    res = client.post("/api/v1/evaluate", json=sample_evaluate_body)
    assert res.status_code == 200
    body = res.json()
    assert body["evaluation_id"]
    assert body["analysis"]["claims"]
    assert body["attribution"]["chains"] is not None
    assert body["evaluation"]["missing_factors"][0]["heading"]
    assert "summary" in body["evaluation"]["missing_factors"][0]
    assert "confidence" not in json.dumps(body)


def test_evaluate_requires_all_criteria(client, sample_evaluate_body: dict) -> None:
    body = {**sample_evaluate_body, "criteria": ["missing_factors"]}
    res = client.post("/api/v1/evaluate", json=body)
    assert res.status_code == 422


def test_no_numeric_score_fields_in_response(client, sample_evaluate_body: dict) -> None:
    res = client.post("/api/v1/evaluate", json=sample_evaluate_body)
    bad_keys: set[str] = set()
    _collect_keys(res.json(), bad_keys)
    assert not bad_keys


def test_golden_fixture_matches_api(client, sample_evaluate_body: dict) -> None:
    res = client.post("/api/v1/evaluate", json=sample_evaluate_body)
    assert res.status_code == 200

    fixture_path = Path(__file__).parent / "fixtures" / "evaluate_response_snitch_example.json"
    if not fixture_path.exists():
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(
            json.dumps(res.json(), indent=2),
            encoding="utf-8",
        )
        pytest.skip("Golden fixture created on first run")
        return

    golden = json.loads(fixture_path.read_text(encoding="utf-8"))
    live = res.json()

    for key in ("analysis", "attribution", "evaluation", "meta"):
        assert key in live
        assert key in golden

    assert len(live["evaluation"]["missing_factors"]) == len(
        golden["evaluation"]["missing_factors"]
    )
    assert live["evaluation"]["missing_factors"][0]["heading"] == (
        golden["evaluation"]["missing_factors"][0]["heading"]
    )
