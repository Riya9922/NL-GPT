from pydantic import BaseModel, Field

from app.models.enums import ClaimType


class TextSpan(BaseModel):
    start: int
    end: int


class Claim(BaseModel):
    id: str
    text: str
    span: TextSpan | None = None
    type: ClaimType


class Assumption(BaseModel):
    id: str
    text: str
    related_claim_ids: list[str] = Field(default_factory=list)
    derived_from_hint: str | None = None


class ReasoningStep(BaseModel):
    id: str
    step: str
    order: int
    supports_claim_ids: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    claims: list[Claim]
    assumptions: list[Assumption]
    reasoning_steps: list[ReasoningStep]
    unsupported_statements: list[str] = Field(default_factory=list)
    completeness_notes: str = ""
