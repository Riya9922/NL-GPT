import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_evaluate_body() -> dict:
    return {
        "user_query": "Should SNITCH open another store in Bangalore?",
        "ai_response": "Bangalore is likely the strongest market. Open another Bangalore store.",
        "criteria": [
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality",
        ],
        "claim_verification_enabled": False,
        "source_preferences": {
            "memory": False,
            "user_context": True,
            "web": True,
            "research": True,
            "company": True,
            "internal": False,
        },
        "regenerate": True,
        "answer_quality_intent": {
            "user_intent": "Decide whether to open another SNITCH store in Bangalore.",
            "expertise_level": "intermediate",
            "user_goal": "Board-ready recommendation with risks called out.",
            "constraints_or_expectations": "Under 500 words; cite only provided sources.",
            "good_answer_looks_like": "Executive summary, then pros/cons, then go/no-go criteria.",
        },
    }
