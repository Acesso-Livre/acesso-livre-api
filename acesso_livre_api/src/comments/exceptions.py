from typing import Optional

from fastapi import HTTPException, status

from func_log import *


class CommentNotFoundException(HTTPException):
    """Exceção levantada quando um comentário não é encontrado."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentário não encontrado",
        )
        log_message("Comentário não encontrado", level="warning")


class CommentStatusInvalidException(HTTPException):
    """Exceção levantada quando o status do comentário é inválido."""

    def __init__(self, invalid_status: Optional[str] = None) -> None:
        if invalid_status:
            detail = f"Status '{invalid_status}' não é válido. Status válidos: 'pending', 'approved', 'rejected'"
            log_message(f"Status inválido fornecido: {invalid_status}", level="warning")
        else:
            detail = "Status fornecido não é válido. Status válidos: 'pending', 'approved', 'rejected'"
            log_message("Status inválido fornecido", level="warning")

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentRatingInvalidException(HTTPException):
    """Exceção levantada quando a avaliação está fora do range válido."""

    def __init__(self, rating: Optional[int] = None) -> None:
        if rating is not None:
            detail = f"Avaliação {rating} está fora do range válido. Avaliações devem estar entre 1 e 5"
            log_message(f"Avaliação inválida fornecida: {rating}", level="warning")
        else:
            detail = "Avaliação deve estar entre 1 e 5"
            log_message("Avaliação inválida fornecida", level="warning")
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentImagesInvalidException(HTTPException):
    """Exceção levantada quando há problemas com as imagens do comentário."""

    def __init__(self, message: Optional[str] = None) -> None:
        if message:
            detail = f"Problema com imagens: {message}"
            log_message(f"Problema com imagens do comentário: {message}", level="warning")
        else:
            detail = "Formato de imagens inválido ou imagem corrompida"
            log_message("Problema com imagens do comentário", level="warning")
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentPermissionDeniedException(HTTPException):
    """Exceção levantada quando operações são realizadas sem permissão adequada."""

    def __init__(self, operation: Optional[str] = None) -> None:
        if operation:
            detail = f"Sem permissão para {operation} do comentário"
            log_message(f"Permissão negada para operação: {operation}", level="warning")
        else:
            detail = "Sem permissão para realizar esta operação no comentário"
            log_message("Permissão negada para operação no comentário", level="warning")
        
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class CommentUpdateException(HTTPException):
    """Exceção levantada quando ocorre erro durante a atualização do comentário."""

    def __init__(self, comment_id: Optional[int] = None) -> None:
        if comment_id:
            detail = f"Erro ao atualizar comentário {comment_id}"
            log_message(f"Erro ao atualizar comentário {comment_id}", level="error")
        else:
            detail = "Erro ao atualizar comentário"
            log_message("Erro ao atualizar comentário", level="error")
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentDeleteException(HTTPException):
    """Exceção levantada quando ocorre erro durante a exclusão do comentário."""

    def __init__(self, comment_id: Optional[int] = None) -> None:
        if comment_id:
            detail = f"Erro ao excluir comentário {comment_id}"
            log_message(f"Erro ao excluir comentário {comment_id}", level="error")
        else:
            detail = "Erro ao excluir comentário"
            log_message("Erro ao excluir comentário", level="error")
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentCreateException(HTTPException):
    """Exceção levantada quando ocorre erro durante a criação do comentário."""

    def __init__(self, reason: Optional[str] = None) -> None:
        if reason:
            detail = f"Erro ao criar comentário: {reason}"
            log_message(f"Erro ao criar comentário: {reason}", level="error")
        else:
            detail = "Erro interno ao processar criação do comentário"
            log_message("Erro ao criar comentário", level="error")
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentNotPendingException(HTTPException):
    """Exceção levantada quando tentativa de aprovação/rejeição é feita em comentário não pendente."""

    def __init__(self, comment_id: Optional[int] = None, current_status: Optional[str] = None) -> None:
        if comment_id and current_status:
            log_message(f"Comentário {comment_id} com status '{current_status}' não pode ser processado", level="warning")
            detail = f"Comentário {comment_id} não pode ser processado pois está com status '{current_status}'. Apenas comentários com status 'pending' podem ser aprovados ou rejeitados"
        elif comment_id:
            log_message(f"Comentário {comment_id} não está com status 'pending'", level="warning")
            detail = f"Comentário {comment_id} não pode ser processado pois não está com status 'pending'"
        else:
            log_message("Comentário não está com status 'pending'", level="warning")
            detail = "Apenas comentários com status 'pending' podem ser aprovados ou rejeitados"
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )

class CommentGenericException(HTTPException):
    """Exceção genérica para erros internos no módulo de comentários."""

    def __init__(self, detail: Optional[str] = None) -> None:
        if not detail:
            log_message("Erro interno no módulo de comentários", level="error")
            detail = "Ocorreu um erro interno no processamento dos comentários."
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )