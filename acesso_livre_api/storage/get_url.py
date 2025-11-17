import logging

logger = logging.getLogger(__name__)
from acesso_livre_api.src.config import settings
from acesso_livre_api.storage.client import supabase_client


def get_public_url(file_path: str) -> str:
    """Returns the public URL for a file in Supabase storage."""
    try:
        client = supabase_client()
        public_url = client.storage.from_(settings.bucket_name).get_public_url(file_path)
        logger.info("Public URL for %s: %s", file_path, public_url)
        return public_url

    except Exception as e:
        logging.error(f"Error getting public URL for {file_path}: {str(e)}")
        raise e


def get_signed_url(file_path: str, expires_in: int = 3600) -> str:
    """Returns a signed URL for a file in Supabase storage that expires after a given time."""
    try:
        client = supabase_client()
        signed_url_response = client.storage.from_(
            settings.bucket_name
        ).create_signed_url(file_path, expires_in)
        signed_url = signed_url_response.get("signedURL")
        return signed_url

    except Exception as e:
        logging.error(f"Error getting signed URL for {file_path}: {str(e)}")
        raise e
