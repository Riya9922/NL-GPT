import logging
import time
import uuid

from app.config import get_settings
from app.models.enums import ALL_CRITERIA, Criteria, EvaluationStatus
from app.models.request import Citation, EvaluationRequest
from app.models.response import EvaluationMeta, EvaluationResponse
from app.services.analysis import analyze
from app.services.attribution import attribute
from app.services.evaluation import evaluate
from app.services.input_normalizer import normalize_user_context
from app.services.regeneration import regenerate
from app.services.validation import validate_evaluation_request

logger = logging.getLogger(__name__)


async def run_evaluation(req: EvaluationRequest) -> EvaluationResponse:
    """Orchestrate full evaluation pipeline: Phase 3 → 3.5 → 4 → 5."""
    started = time.perf_counter()
    settings = get_settings()
    settings.require_llm_key_when_live()
    validate_evaluation_request(req, settings)

    normalized_context = await normalize_user_context(req)
    if normalized_context is not None:
        req = req.model_copy(update={"user_context": normalized_context})

    # Auto-search for web sources if enabled and no sources provided
    if settings.enable_web_search and req.claim_verification_enabled:
        from app.services.web_search import auto_search_sources
        
        # Extract claims first to know what to search for
        logger.info("🔍 Auto-searching for web sources...")
        preliminary_analysis = await analyze(req)
        claim_texts = [c.text for c in preliminary_analysis.claims[:5]]
        
        # Search for sources
        web_sources = await auto_search_sources(
            claim_texts,
            req.user_query,
            settings
        )
        
        # Add web sources as citations
        if web_sources:
            logger.info(f"✅ Found {len(web_sources)} web sources")
            new_citations = list(req.citations)
            for i, source in enumerate(web_sources):
                new_citations.append(
                    Citation(
                        index=len(new_citations) + 1,
                        title=source.get("title"),
                        url=source.get("url"),
                        raw=source.get("snippet"),
                    )
                )
            req = req.model_copy(update={"citations": new_citations})

    # Phase 3: Extract claims, assumptions, reasoning steps
    analysis = await analyze(req)
    
    # Phase 3.5: Build attribution chains
    attribution = await attribute(req, analysis)
    
    # Phase 4: Evaluate across all dimensions
    evaluation = await evaluate(req, analysis, attribution)
    
    # Phase 5: Regeneration (optional, triggered by criteria + flag)
    regeneration = await regenerate(req, analysis, attribution, evaluation)
        
    duration_ms = int((time.perf_counter() - started) * 1000)

    return EvaluationResponse(
        evaluation_id=str(uuid.uuid4()),
        status=EvaluationStatus.COMPLETED,
        analysis=analysis,
        attribution=attribution,
        evaluation=evaluation,
        regeneration=regeneration,
        meta=EvaluationMeta(
            model="mock" if settings.mock_mode else settings.llm_model_eval,
            duration_ms=duration_ms,
            claim_verification_enabled=req.claim_verification_enabled,
            dimensions=list(ALL_CRITERIA),
        ),
    )
