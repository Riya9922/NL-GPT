from pydantic import BaseModel, Field

from app.models.enums import Criteria


class RegenerationResult(BaseModel):
    improved_answer: str
    changes_summary: list[str] = Field(default_factory=list)
    recommended_inputs: list[str] = Field(default_factory=list)
    addressed_criteria: list[Criteria] = Field(default_factory=list)
