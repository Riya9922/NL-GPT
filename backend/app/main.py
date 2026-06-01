import logging
import traceback

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.adapters.groq_client import verify_groq_connection
from app.config import get_settings
from app.errors import AppError
from app.models.analysis import AnalysisResult
from app.models.attribution import AttributionResult
from app.models.request import EvaluationRequest
from app.models.response import EvaluationResponse
from app.services.analysis import analyze as run_analyze
from app.services.attribution import attribute as run_attribute
from app.models.upload import UploadResponse
from app.orchestrator import run_evaluation
from app.services.upload_service import save_upload
from app.services.url_fetch import fetch_url_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="AI Output Evaluation API",
    version="0.2.0",
    description="Evaluate AI outputs — Phase 2 input collection",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "detail": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc) or "Internal server error",
            "hint": (
                "Ensure the API is running (uvicorn from backend/). "
                "With MOCK_MODE=true, GROQ_API_KEY is optional."
            ),
        },
    )


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "mock_mode": settings.mock_mode,
        "llm_provider": settings.llm_provider,
    }


@app.get("/health/groq")
async def health_groq() -> dict[str, str]:
    if settings.mock_mode:
        return {
            "status": "skipped",
            "message": "MOCK_MODE=true — Groq not required for /evaluate",
        }
    try:
        settings.require_llm_key_when_live()
        return await verify_groq_connection(settings)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


class FetchUrlRequest(BaseModel):
    url: str = Field(..., min_length=8)


class FetchUrlResponse(BaseModel):
    url: str
    text_preview: str
    char_count: int


@app.post("/api/v1/uploads", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    stored = await save_upload(file)
    return UploadResponse(
        file_id=stored.file_id,
        filename=stored.filename,
        extracted_chars=len(stored.extracted_text),
    )


@app.post("/api/v1/context/fetch-url", response_model=FetchUrlResponse)
async def fetch_url(body: FetchUrlRequest) -> FetchUrlResponse:
    text = await fetch_url_text(body.url)
    preview = text[:500] + ("…" if len(text) > 500 else "")
    return FetchUrlResponse(url=body.url, text_preview=preview, char_count=len(text))


class AttributeRequestBody(BaseModel):
    analysis: AnalysisResult
    evaluate: EvaluationRequest


@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_endpoint(request: EvaluationRequest) -> AnalysisResult:
    from app.services.validation import validate_evaluation_request

    validate_evaluation_request(request, get_settings())
    return await run_analyze(request)


@app.post("/api/v1/attribute", response_model=AttributionResult)
async def attribute_endpoint(body: AttributeRequestBody) -> AttributionResult:
    """Build attribution chains from analysis + evaluate context."""
    from app.services.validation import validate_evaluation_request

    validate_evaluation_request(body.evaluate, get_settings())
    return await run_attribute(body.evaluate, body.analysis)


@app.post("/api/v1/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    return await run_evaluation(request)
