import asyncio
import logging
from cachetools import TTLCache
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
from acesso_livre_api.src.config import settings
from acesso_livre_api.storage.client import supabase_client

_semaphore = asyncio.Semaphore(10)  # Máximo 10 requisições paralelas

# Cache de signed URLs: max 1000 URLs, TTL de 55 minutos (5 min antes de expirar)
_url_cache: TTLCache = TTLCache(maxsize=1000, ttl=3300)
_cache_lock = asyncio.Lock()


async def get_signed_url(file_path: str, expires_in: int = 3600) -> str:
    """Returns a signed URL for a file in Supabase storage that expires after a given time.
    
    Uses in-memory cache to avoid repeated calls to Supabase for the same file.
    Cache TTL is 55 minutes (5 minutes before the signed URL expires).
    """
    # Verificar cache primeiro
    cache_key = f"{file_path}:{expires_in}"
    
    async with _cache_lock:
        if cache_key in _url_cache:
            logger.debug(f"Cache HIT for {file_path}")
            return _url_cache[cache_key]
    
    async with _semaphore:  # Controla concorrência
        try:
            # Double-check cache após adquirir semaphore (outra task pode ter preenchido)
            async with _cache_lock:
                if cache_key in _url_cache:
                    return _url_cache[cache_key]

            def _get_signed_url():
                client = supabase_client()
                signed_url_response = client.storage.from_(
                    settings.bucket_name
                ).create_signed_url(file_path, expires_in)
                return signed_url_response.get("signedURL")

            signed_url = await run_in_threadpool(_get_signed_url)
            
            # Armazenar no cache
            async with _cache_lock:
                _url_cache[cache_key] = signed_url
                logger.debug(f"Cache MISS - stored URL for {file_path}")
            
            return signed_url

        except Exception as e:
            error_str = str(e)
            # Handle gracefully when file doesn't exist in storage
            if "not_found" in error_str.lower() or "Object not found" in error_str:
                logger.warning(f"File not found in storage: {file_path}")
                return None
            logging.error(f"Error getting signed URL for {file_path}: {error_str}")
            raise e


async def get_signed_urls(file_paths: list[str], expires_in: int = 3600) -> list[str]:
    """Returns a list of signed URLs for multiple files in Supabase storage.
    
    Files that don't exist in storage are filtered out from the result.
    """
    if not file_paths:
        return []

    signed_urls = await asyncio.gather(
        *[get_signed_url(path, expires_in) for path in file_paths]
    )

    # Filter out None values (files that weren't found)
    return [url for url in signed_urls if url is not None]
