from typing import Optional

from fastapi import HTTPException, status


class CommentNotFoundException(HTTPException):
    """Exceção levantada quando um comentário não é encontrado."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentário não encontrado",
        )


class CommentStatusInvalidException(HTTPException):
    """Exceção levantada quando o status do comentário é inválido."""

    def __init__(self, invalid_status: Optional[str] = None) -> None:
        if invalid_status:
            detail = f"Status '{invalid_status}' não é válido. Status válidos: 'pending', 'approved', 'rejected'"
        else:
            detail = "Status fornecido não é válido. Status válidos: 'pending', 'approved', 'rejected'"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentRatingInvalidException(HTTPException):
    """Exceção levantada quando a avaliação está fora do range válido."""

    def __init__(self, rating: Optional[int] = None) -> None:
        if rating is not None:
            detail = f"Avaliação {rating} está fora do range válido. Avaliações devem estar entre 1 e 5"
        else:
            detail = "Avaliação deve estar entre 1 e 5"
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentImagesInvalidException(HTTPException):
    """Exceção levantada quando há problemas com as imagens do comentário."""

    def __init__(self, message: Optional[str] = None) -> None:
        if message:
            detail = f"Problema com imagens: {message}"
        else:
            detail = "Formato de imagens inválido ou imagem corrompida"
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )


class CommentPermissionDeniedException(HTTPException):
    """Exceção levantada quando operações são realizadas sem permissão adequada."""

    def __init__(self, operation: Optional[str] = None) -> None:
        if operation:
            detail = f"Sem permissão para {operation} do comentário"
        else:
            detail = "Sem permissão para realizar esta operação no comentário"
        
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class CommentUpdateException(HTTPException):
    """Exceção levantada quando ocorre erro durante a atualização do comentário."""

    def __init__(self, comment_id: Optional[int] = None) -> None:
        if comment_id:
            detail = f"Erro ao atualizar comentário {comment_id}"
        else:
            detail = "Erro ao atualizar comentário"
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentDeleteException(HTTPException):
    """Exceção levantada quando ocorre erro durante a exclusão do comentário."""

    def __init__(self, comment_id: Optional[int] = None) -> None:
        if comment_id:
            detail = f"Erro ao excluir comentário {comment_id}"
        else:
            detail = "Erro ao excluir comentário"
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentCreateException(HTTPException):
    """Exceção levantada quando ocorre erro durante a criação do comentário."""

    def __init__(self, reason: Optional[str] = None) -> None:
        if reason:
            detail = f"Erro ao criar comentário: {reason}"
        else:
            detail = "Erro interno ao processar criação do comentário"
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class CommentNotPendingException(HTTPException):
    """Exceção levantada quando tentativa de aprovação/rejeição é feita em comentário não pendente."""

    def __init__(self, comment_id: Optional[int] = None, current_status: Optional[str] = None) -> None:
        if comment_id and current_status:
            detail = f"Comentário {comment_id} não pode ser processado pois está com status '{current_status}'. Apenas comentários com status 'pending' podem ser aprovados ou rejeitados"
        elif comment_id:
            detail = f"Comentário {comment_id} não pode ser processado pois não está com status 'pending'"
        else:
            detail = "Apenas comentários com status 'pending' podem ser aprovados ou rejeitados"
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail,
        )

class CommentGenericException(HTTPException):
    """Exceção genérica para erros internos no módulo de comentários."""

    def __init__(self, detail: Optional[str] = None) -> None:
        if not detail:
            detail = "Ocorreu um erro interno no processamento dos comentários."
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )