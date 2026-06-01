from enum import Enum


class Criteria(str, Enum):
    CLAIM_VERIFICATION = "claim_verification"
    SOURCE_TRANSPARENCY = "source_transparency"
    LOGIC_REASONING = "logic_reasoning"
    MISSING_FACTORS = "missing_factors"
    IMPROVE_ANSWER_QUALITY = "improve_answer_quality"


ALL_CRITERIA: list[Criteria] = list(Criteria)


class ClaimType(str, Enum):
    FACTUAL = "factual"
    OPINION = "opinion"
    PREDICTION = "prediction"


class ClaimVerificationStatus(str, Enum):
    VERIFIED = "verified"
    NEEDS_VERIFICATION = "needs_verification"
    UNSUPPORTED = "unsupported"
    NOT_APPLICABLE = "not_applicable"


class SourceType(str, Enum):
    MEMORY = "memory"
    USER_CONTEXT = "user_context"
    WEB = "web"
    RESEARCH = "research"
    COMPANY = "company"
    INTERNAL = "internal"
    CUSTOM = "custom"


class EvaluationStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
