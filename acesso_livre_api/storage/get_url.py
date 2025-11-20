import asyncio
import logging
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
from acesso_livre_api.src.config import settings
from acesso_livre_api.storage.client import supabase_client

_semaphore = asyncio.Semaphore(10)  # Máximo 10 requisições paralelas


async def get_signed_url(file_path: str, expires_in: int = 3600) -> str:
    """Returns a signed URL for a file in Supabase storage that expires after a given time."""
    async with _semaphore:  # Controla concorrência
        try:

            def _get_signed_url():
                client = supabase_client()
                signed_url_response = client.storage.from_(
                    settings.bucket_name
                ).create_signed_url(file_path, expires_in)
                return signed_url_response.get("signedURL")

            signed_url = await run_in_threadpool(_get_signed_url)
            return signed_url

        except Exception as e:
            logging.error(f"Error getting signed URL for {file_path}: {str(e)}")
            raise e


async def get_signed_urls(file_paths: list[str], expires_in: int = 3600) -> list[str]:
    """Returns a list of signed URLs for multiple files in Supabase storage."""
    if not file_paths:
        return []

    signed_urls = await asyncio.gather(
        *[get_signed_url(path, expires_in) for path in file_paths]
    )

    return signed_urls
