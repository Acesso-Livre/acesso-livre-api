import pytest

from acesso_livre_api.src.comments.exceptions import (
    CommentCreateException,
    CommentDeleteException,
    CommentGenericException,
    CommentImagesInvalidException,
    CommentNotFoundException,
    CommentNotPendingException,
    CommentPermissionDeniedException,
    CommentRatingInvalidException,
    CommentStatusInvalidException,
    CommentUpdateException,
)


def test_comment_not_found_exception():
    """Testa CommentNotFoundException."""
    exc = CommentNotFoundException()
    assert exc.status_code == 404
    assert exc.detail == "Comentário não encontrado"


def test_comment_status_invalid_exception():
    """Testa CommentStatusInvalidException."""
    exc = CommentStatusInvalidException("invalid_status")
    assert exc.status_code == 422
    assert "invalid_status" in exc.detail

    exc_default = CommentStatusInvalidException()
    assert exc_default.status_code == 422
    assert "não é válido" in exc_default.detail


def test_comment_rating_invalid_exception():
    """Testa CommentRatingInvalidException."""
    exc = CommentRatingInvalidException(6)
    assert exc.status_code == 422
    assert "6" in exc.detail

    exc_default = CommentRatingInvalidException()
    assert exc_default.status_code == 422
    assert "deve estar entre 1 e 5" in exc_default.detail


def test_comment_images_invalid_exception():
    """Testa CommentImagesInvalidException."""
    exc = CommentImagesInvalidException("Invalid image format")
    assert exc.status_code == 422
    assert "Invalid image format" in exc.detail

    exc_default = CommentImagesInvalidException()
    assert exc_default.status_code == 422
    assert "Formato de imagens inválido" in exc_default.detail


def test_comment_permission_denied_exception():
    """Testa CommentPermissionDeniedException."""
    exc = CommentPermissionDeniedException("excluir")
    assert exc.status_code == 403
    assert "excluir" in exc.detail

    exc_default = CommentPermissionDeniedException()
    assert exc_default.status_code == 403
    assert "realizar esta operação" in exc_default.detail


def test_comment_update_exception():
    """Testa CommentUpdateException."""
    exc = CommentUpdateException(123)
    assert exc.status_code == 500
    assert "123" in exc.detail

    exc_default = CommentUpdateException()
    assert exc_default.status_code == 500
    assert "Erro ao atualizar comentário" in exc_default.detail


def test_comment_delete_exception():
    """Testa CommentDeleteException."""
    exc = CommentDeleteException(456)
    assert exc.status_code == 500
    assert "456" in exc.detail

    exc_default = CommentDeleteException()
    assert exc_default.status_code == 500
    assert "Erro ao excluir comentário" in exc_default.detail


def test_comment_create_exception():
    """Testa CommentCreateException."""
    exc = CommentCreateException("Database error")
    assert exc.status_code == 500
    assert "Database error" in exc.detail

    exc_default = CommentCreateException()
    assert exc_default.status_code == 500
    assert "Erro interno ao processar criação do comentário" in exc_default.detail


def test_comment_not_pending_exception():
    """Testa CommentNotPendingException."""
    exc = CommentNotPendingException(789, "approved")
    assert exc.status_code == 422
    assert "789" in exc.detail
    assert "approved" in exc.detail

    exc_partial = CommentNotPendingException(789)
    assert exc_partial.status_code == 422
    assert "789" in exc_partial.detail

    exc_default = CommentNotPendingException()
    assert exc_default.status_code == 422
    assert "Apenas comentários com status 'pending'" in exc_default.detail


def test_comment_generic_exception():
    """Testa CommentGenericException."""
    exc = CommentGenericException("Custom error message")
    assert exc.status_code == 500
    assert exc.detail == "Custom error message"

    exc_default = CommentGenericException()
    assert exc_default.status_code == 500
    assert "Ocorreu um erro interno no processamento dos comentários" in exc_default.detail