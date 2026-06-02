from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent

# Repo-root .env first, then backend/.env (later files override — local wins)
_env_candidates = [_PROJECT_ROOT / ".env", _BACKEND_DIR / ".env"]
_env_files = tuple(str(p) for p in _env_candidates if p.is_file())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files or str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "groq"
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        validation_alias="GROQ_BASE_URL",
    )
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")
    llm_model_analysis: str = "llama-3.1-8b-instant"
    llm_model_eval: str = "llama-3.3-70b-versatile"
    llm_model_regen: str = "llama-3.3-70b-versatile"
    search_api_key: str | None = None
    enable_web_search: bool = True  # Enable automatic web search for source verification
    max_response_chars: int = 32_000
    max_claims: int = 40
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    mock_mode: bool = True

    @model_validator(mode="after")
    def normalize_provider(self) -> "Settings":
        self.llm_provider = self.llm_provider.lower().strip()
        return self

    @property
    def effective_llm_api_key(self) -> str | None:
        if self.llm_provider == "groq":
            return self.groq_api_key or self.llm_api_key
        return self.llm_api_key

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def require_llm_key_when_live(self) -> None:
        if self.mock_mode:
            return
        if not self.effective_llm_api_key:
            raise ValueError(
                "GROQ_API_KEY is required when MOCK_MODE=false. "
                "Add your key to backend/.env or set MOCK_MODE=true for mock responses."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
