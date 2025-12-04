import asyncio
import logging
from fastapi.concurrency import run_in_threadpool
from acesso_livre_api.storage.client import supabase_client
from acesso_livre_api.src.config import settings

logger = logging.getLogger(__name__)

_semaphore = asyncio.Semaphore(10)  # Máximo 10 requisições paralelas


async def delete_image(file_path: str) -> bool:
    """Deleta uma imagem do Supabase storage.
    
    Args:
        file_path: Nome do arquivo a ser deletado (ex: "uuid.jpg")
    
    Returns:
        True se a deleção foi bem sucedida, False caso contrário
    """
    async with _semaphore:
        try:
            def _delete_image():
                client = supabase_client()
                response = client.storage.from_(settings.bucket_name).remove([file_path])
                return response

            await run_in_threadpool(_delete_image)
            logger.info(f"Imagem {file_path} deletada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar imagem {file_path}: {str(e)}")
            return False


async def delete_images(file_paths: list[str]) -> bool:
    """Deleta múltiplas imagens do Supabase storage.
    
    Args:
        file_paths: Lista de nomes de arquivos a serem deletados
    
    Returns:
        True se todas as deleções foram bem sucedidas, False se alguma falhou
    """
    if not file_paths:
        return True

    results = await asyncio.gather(
        *[delete_image(path) for path in file_paths],
        return_exceptions=True
    )

    # Verifica se todas as deleções foram bem sucedidas
    success = all(result is True for result in results)
    
    if not success:
        failed_count = sum(1 for r in results if r is not True)
        logger.warning(f"{failed_count} de {len(file_paths)} imagens falharam ao deletar")
    
    return success
