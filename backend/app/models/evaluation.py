from pydantic import BaseModel, Field

from app.models.enums import ClaimVerificationStatus, SourceType


class VerificationSource(BaseModel):
    title: str
    url: str | None = None
    source_type: SourceType
    snippet: str | None = None


class EvaluatedClaim(BaseModel):
    claim_id: str
    status: ClaimVerificationStatus
    sources: list[VerificationSource] = Field(default_factory=list)
    verification_note: str | None = None


class SourceUsedItem(BaseModel):
    source_type: SourceType
    label: str
    url: str | None = None


class SourceAnalysis(BaseModel):
    sources_used: list[SourceUsedItem] = Field(default_factory=list)
    trust_issues: list[str] = Field(default_factory=list)
    missing_source_types: list[str] = Field(default_factory=list)


class EvidenceLink(BaseModel):
    url: str | None = None
    label: str


class ReasoningPathStep(BaseModel):
    step_id: str
    text: str
    evidence_links: list[EvidenceLink] = Field(default_factory=list)
    expandable_detail: str | None = None


class LogicEvaluation(BaseModel):
    conclusion: str = ""
    reasoning_path: list[ReasoningPathStep] = Field(default_factory=list)
    logical_gaps: list[str] = Field(default_factory=list)
    alternate_perspectives: list[str] = Field(default_factory=list)
    critique: str = ""


class MissingFactor(BaseModel):
    heading: str
    summary: str = Field(..., max_length=200)


class AnswerQualityNotes(BaseModel):
    clarity_note: str | None = None
    completeness_note: str | None = None
    actionability_note: str | None = None
    summary: str | None = None


class EvaluationResult(BaseModel):
    claims: list[EvaluatedClaim] = Field(default_factory=list)
    source_analysis: SourceAnalysis = Field(default_factory=SourceAnalysis)
    logic: LogicEvaluation = Field(default_factory=LogicEvaluation)
    missing_factors: list[MissingFactor] = Field(default_factory=list)
    answer_quality: AnswerQualityNotes | None = None
