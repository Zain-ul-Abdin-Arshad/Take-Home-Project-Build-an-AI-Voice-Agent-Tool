from functools import lru_cache
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv


class Settings(BaseModel):
    app_name: str = Field(default="AI Voice Agent Backend")
    environment: str = Field(default=os.getenv("ENV", "development"))

    supabase_url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))

    retell_api_key: str = Field(default_factory=lambda: os.getenv("RETELL_API_KEY", ""))
    retell_base_url: str = Field(default_factory=lambda: os.getenv("RETELL_BASE_URL", "https://api.retellai.com"))
    retell_start_call_path: str = Field(default_factory=lambda: os.getenv("RETELL_START_CALL_PATH", "/v2/create-phone-call"))
    retell_reply_path: str = Field(default_factory=lambda: os.getenv("RETELL_REPLY_PATH", "/v2/calls/reply"))
    retell_from_number: str = Field(default_factory=lambda: os.getenv("RETELL_FROM_NUMBER", ""))
    webhook_base_url: str = Field(default_factory=lambda: os.getenv("WEBHOOK_BASE_URL", "https://your-domain.com"))

    # OpenAI
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    # Google Gemini
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))


@lru_cache(maxsize=1)
def get_settings() -> "Settings":
    # Load .env once
    load_dotenv(override=False)
    return Settings()


__all__ = ["Settings", "get_settings"]


