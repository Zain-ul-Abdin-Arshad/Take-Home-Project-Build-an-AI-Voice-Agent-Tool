from typing import Optional
from supabase import create_client, Client
from .settings import Settings


_client: Optional[Client] = None


def get_supabase(settings: Settings) -> Client:
    global _client
    if _client is not None:
        return _client
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("Supabase credentials are not configured")
    _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


__all__ = ["get_supabase"]


