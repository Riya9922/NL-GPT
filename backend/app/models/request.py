from pydantic import BaseModel, Field, field_validator

from app.models.enums import ALL_CRITERIA, Criteria


class SourcePreferences(BaseModel):
    memory: bool = True
    user_context: bool = True
    web: bool = True
    research: bool = True
    company: bool = True
    internal: bool = True


class CustomSource(BaseModel):
    label: str
    url: str | None = None
    notes: str | None = None


class UserContext(BaseModel):
    file_ids: list[str] = Field(default_factory=list)
    pasted_text: str = ""
    urls: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    index: int
    title: str | None = None
    url: str | None = None
    raw: str | None = None


class AnswerQualityIntent(BaseModel):
    user_intent: str | None = None
    expertise_level: str | None = None
    user_goal: str | None = None
    constraints_or_expectations: str | None = None
    good_answer_looks_like: str | None = None


class EvaluationRequest(BaseModel):
    user_query: str | None = None
    ai_response: str = Field(..., min_length=1)
    conversation_id: str | None = None
    criteria: list[Criteria]
    claim_verification_enabled: bool = False
    source_preferences: SourcePreferences
    custom_sources: list[CustomSource] = Field(default_factory=list)
    user_context: UserContext | None = None
    citations: list[Citation] = Field(default_factory=list)
    regenerate: bool = True
    answer_quality_intent: AnswerQualityIntent | None = None

    @field_validator("criteria")
    @classmethod
    def criteria_must_include_all_dimensions(cls, value: list[Criteria]) -> list[Criteria]:
        required = {c.value for c in ALL_CRITERIA}
        provided = {c.value if isinstance(c, Criteria) else c for c in value}
        if provided != required:
            missing = required - provided
            extra = provided - required
            parts: list[str] = []
            if missing:
                parts.append(f"missing: {sorted(missing)}")
            if extra:
                parts.append(f"unexpected: {sorted(extra)}")
            raise ValueError(
                "criteria must include all five evaluation dimensions. " + "; ".join(parts)
            )
        return value
