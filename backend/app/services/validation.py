from app.config import Settings
from app.errors import AppError
from app.models.enums import ALL_CRITERIA
from app.models.request import EvaluationRequest


def validate_evaluation_request(req: EvaluationRequest, settings: Settings) -> None:
    if not req.ai_response.strip():
        raise AppError("EMPTY_RESPONSE", "ai_response cannot be empty", 400)

    required = {c.value for c in ALL_CRITERIA}
    provided = {c.value if hasattr(c, "value") else c for c in req.criteria}
    if provided != required:
        raise AppError(
            "INCOMPLETE_DIMENSIONS",
            "criteria must include all five evaluation dimensions",
            400,
        )

    if len(req.ai_response) > settings.max_response_chars:
        raise AppError(
            "RESPONSE_TOO_LONG",
            (
                f"ai_response exceeds MAX_RESPONSE_CHARS ({settings.max_response_chars}). "
                "Shorten the text or split the evaluation."
            ),
            413,
        )
