import os

from acesso_livre_api.src.comments import schemas
from acesso_livre_api.storage.get_url import get_signed_urls


def extract_image_id(file_path: str) -> str:
    """Extrai o UUID do nome do arquivo (remove a extensão).
    
    Ex: '6a9c217f-3d21-4a90-896a-2a2cb3dc53a8.png' -> '6a9c217f-3d21-4a90-896a-2a2cb3dc53a8'
    """
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0]
    return name_without_ext


async def get_images_with_ids(file_paths: list[str]) -> list[schemas.ImageResponse]:
    """Converte lista de paths em lista de ImageResponse com IDs e signed URLs."""
    if not file_paths:
        return []
    
    signed_urls = await get_signed_urls(file_paths)
    
    # Filter out images where signed URL generation failed (None)
    return [
        schemas.ImageResponse(
            id=extract_image_id(path),
            url=url
        )
        for path, url in zip(file_paths, signed_urls) if url is not None
    ]


def find_image_path_by_id(images: list[str], image_id: str) -> str | None:
    """Encontra o path completo da imagem pelo ID (UUID)."""
    for path in images:
        if extract_image_id(path) == image_id:
            return path
    return None
