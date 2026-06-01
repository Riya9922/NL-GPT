from app.models.request import EvaluationRequest, UserContext
from app.services.context_store import context_store
from app.services.url_fetch import fetch_url_text


async def normalize_user_context(req: EvaluationRequest) -> UserContext | None:
    if not req.user_context:
        return None

    ctx = req.user_context
    parts: list[str] = []

    if ctx.pasted_text.strip():
        parts.append(ctx.pasted_text.strip())

    for file_id in ctx.file_ids:
        stored = context_store.get(file_id)
        if stored and stored.extracted_text:
            parts.append(f"--- {stored.filename} ---\n{stored.extracted_text}")

    for url in ctx.urls:
        url = url.strip()
        if not url:
            continue
        text = await fetch_url_text(url)
        parts.append(f"--- {url} ---\n{text}")

    merged = "\n\n".join(parts)
    return UserContext(
        file_ids=ctx.file_ids,
        pasted_text=merged,
        urls=ctx.urls,
    )
