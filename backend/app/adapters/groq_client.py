"""Groq via OpenAI-compatible HTTP API."""

from openai import AsyncOpenAI

from app.config import Settings


def create_groq_client(settings: Settings) -> AsyncOpenAI:
    api_key = settings.effective_llm_api_key
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set")
    return AsyncOpenAI(
        api_key=api_key,
        base_url=settings.groq_base_url,
    )


async def verify_groq_connection(settings: Settings) -> dict[str, str]:
    """Lightweight connectivity check (lists models)."""
    client = create_groq_client(settings)
    models = await client.models.list()
    first = models.data[0].id if models.data else "unknown"
    return {"status": "ok", "provider": "groq", "sample_model": first}
