import supabase

from acesso_livre_api.src.config import settings


def supabase_client() -> supabase.AClient:
    """Create and return a Supabase client using settings from the configuration."""
    url: str = settings.bucket_endpoint_url
    key: str = settings.bucket_secret_key
    client: supabase.AClient = supabase.create_client(url, key)
    return client
