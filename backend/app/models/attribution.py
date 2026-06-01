from pydantic import BaseModel, Field

from app.models.enums import SourceType


class ReasoningStepRef(BaseModel):
    step_id: str | None = None
    text: str | None = None


class SourceRef(BaseModel):
    source_id: str | None = None
    source_type: SourceType | None = None
    label: str
    url: str | None = None
    citation_index: int | None = None


class EvidenceItem(BaseModel):
    text: str
    excerpt: str | None = None


class EvidenceBundle(BaseModel):
    supporting: list[EvidenceItem] = Field(default_factory=list)
    counter: list[EvidenceItem] = Field(default_factory=list)


class AssumptionAttribution(BaseModel):
    text: str
    derived_from: str | None = None
    supporting_evidence: str | None = None
    counter_evidence: str | None = None


class ClaimAttributionChain(BaseModel):
    claim_id: str
    claim_text: str
    reasoning_step: ReasoningStepRef | None = None
    source: SourceRef | None = None
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)
    assumption: AssumptionAttribution | None = None
    attribution_gap: str | None = None


class AttributionMeta(BaseModel):
    sources_respected: list[str] = Field(default_factory=list)
    chains_complete: int = 0
    chains_with_gaps: int = 0


class AttributionResult(BaseModel):
    chains: list[ClaimAttributionChain] = Field(default_factory=list)
    unlinked_claims: list[str] = Field(default_factory=list)
    meta: AttributionMeta = Field(default_factory=AttributionMeta)
