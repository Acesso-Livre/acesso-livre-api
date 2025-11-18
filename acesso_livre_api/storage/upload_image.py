import logging
import uuid
from fastapi import UploadFile
from acesso_livre_api.storage.client import supabase_client
from acesso_livre_api.storage.dependencies import ALLOWED_MIME_TYPES


async def upload_image(file: UploadFile) -> str:
    """Uploads an image file to Supabase storage and returns the unique_filename."""
    try:
        client = supabase_client()
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_content = file.file.read()

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError("Unsupported file type")

        await client.storage.from_("acesso-livre-bucket").upload(
            path=unique_filename,
            file=file_content,
            file_options={"content-type": file.content_type},
        )

        return unique_filename

    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")
        raise e
