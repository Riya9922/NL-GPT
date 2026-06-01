from pydantic import BaseModel, Field

from app.models.analysis import AnalysisResult
from app.models.attribution import AttributionResult
from app.models.enums import Criteria, EvaluationStatus
from app.models.evaluation import EvaluationResult
from app.models.regeneration import RegenerationResult


class EvaluationMeta(BaseModel):
    model: str = "mock"
    duration_ms: int = 0
    claim_verification_enabled: bool = False
    dimensions: list[Criteria] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    evaluation_id: str
    status: EvaluationStatus
    analysis: AnalysisResult
    attribution: AttributionResult
    evaluation: EvaluationResult
    regeneration: RegenerationResult | None = None
    meta: EvaluationMeta
