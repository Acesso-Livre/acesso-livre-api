from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from acesso_livre_api.src.comments import schemas
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
from acesso_livre_api.src.comments.service import (
    create_comment,
    delete_comment,
    get_all_comments_by_location_id,
    get_comment,
    get_comments_with_status_pending,
    update_comment_status,
)


@pytest.fixture
def mock_db():
    """Mock do banco de dados."""
    return Mock()


@pytest.fixture
def sample_comment_data():
    """Dados de exemplo para comentário."""
    return schemas.CommentCreate(
        user_name="Test User",
        rating=5,
        comment="Test comment",
        location_id=1,
        images=[],
    )


class TestCreateComment:
    """Testes para create_comment."""

    def test_create_comment_success(self, mock_db, sample_comment_data):
        """Testa criação bem-sucedida de comentário."""
        mock_comment = Mock()
        mock_comment.id = 1
        mock_comment.status = "pending"

        with (
            patch("acesso_livre_api.src.comments.service.get_location_by_id"),
            patch(
                "acesso_livre_api.src.comments.service.models.Comment"
            ) as mock_comment_class,
            patch("acesso_livre_api.src.comments.service.datetime") as mock_datetime,
        ):

            mock_comment_class.return_value = mock_comment
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = create_comment(mock_db, sample_comment_data)

            assert result == mock_comment
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    def test_create_comment_rating_invalid(self, mock_db):
        """Testa erro de avaliação inválida."""
        mock_comment_data = Mock()
        mock_comment_data.rating = 6
        with pytest.raises(CommentRatingInvalidException):
            create_comment(mock_db, mock_comment_data)

    def test_create_comment_images_invalid(self, mock_db):
        """Testa erro de imagens inválidas."""
        invalid_data = schemas.CommentCreate(
            user_name="Test", rating=5, comment="Test", location_id=1, images=[""]
        )

        with pytest.raises(CommentImagesInvalidException):
            create_comment(mock_db, invalid_data)

    def test_create_comment_db_error(self, mock_db, sample_comment_data):
        """Testa erro de banco de dados."""
        with (
            patch("acesso_livre_api.src.comments.service.get_location_by_id"),
            patch("acesso_livre_api.src.comments.service.models.Comment"),
            patch("acesso_livre_api.src.comments.service.datetime"),
        ):

            mock_db.commit.side_effect = SQLAlchemyError("DB Error")

            with pytest.raises(CommentCreateException):
                create_comment(mock_db, sample_comment_data)


class TestGetComment:
    """Testes para get_comment."""

    def test_get_comment_success(self, mock_db):
        """Testa obtenção bem-sucedida de comentário."""
        mock_comment = Mock()
        mock_comment.images = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        result = get_comment(mock_db, 1)

        assert result == mock_comment
        assert mock_comment.images == []

    def test_get_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(CommentNotFoundException):
            get_comment(mock_db, 1)

    def test_get_comment_generic_error(self, mock_db):
        """Testa erro genérico."""
        mock_db.query.side_effect = Exception("Generic error")

        with pytest.raises(CommentNotFoundException):
            get_comment(mock_db, 1)


class TestGetCommentsWithStatusPending:
    """Testes para get_comments_with_status_pending."""

    def test_get_comments_pending_success(self, mock_db):
        """Testa obtenção bem-sucedida de comentários pendentes."""
        mock_comments = [Mock(), Mock()]
        mock_comments[0].images = None
        mock_comments[1].images = ["image.jpg"]

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_comments
        )

        result = get_comments_with_status_pending(mock_db)

        assert result == mock_comments
        assert mock_comments[0].images == []
        assert mock_comments[1].images == ["image.jpg"]

    def test_get_comments_pending_empty(self, mock_db):
        """Testa lista vazia de comentários pendentes."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = get_comments_with_status_pending(mock_db)

        assert result == []

    def test_get_comments_pending_error(self, mock_db):
        """Testa erro ao buscar comentários pendentes."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.side_effect = Exception(
            "DB Error"
        )

        with pytest.raises(CommentGenericException):
            get_comments_with_status_pending(mock_db)


class TestUpdateCommentStatus:
    """Testes para update_comment_status."""

    def test_update_comment_status_success(self, mock_db):
        """Testa atualização bem-sucedida de status."""
        mock_comment = Mock()
        mock_comment.status.value = "pending"
        mock_comment.images = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        update_data = schemas.CommentUpdateStatus(status="approved")

        result = update_comment_status(mock_db, 1, update_data)

        assert result == mock_comment
        assert mock_comment.status == "approved"
        assert mock_comment.images == []
        mock_db.commit.assert_called_once()

    def test_update_comment_status_invalid_status(self, mock_db):
        """Testa status inválido."""
        mock_update_data = Mock()
        mock_update_data.status.value = "invalid_status"

        with pytest.raises(CommentStatusInvalidException):
            update_comment_status(mock_db, 1, mock_update_data)

    def test_update_comment_status_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        update_data = schemas.CommentUpdateStatus(status="approved")

        with pytest.raises(CommentNotFoundException):
            update_comment_status(mock_db, 1, update_data)

    def test_update_comment_status_not_pending(self, mock_db):
        """Testa comentário que não está pendente."""
        mock_comment = Mock()
        mock_comment.status.value = "approved"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        update_data = schemas.CommentUpdateStatus(status="rejected")

        with pytest.raises(CommentNotPendingException):
            update_comment_status(mock_db, 1, update_data)

    def test_update_comment_status_db_error(self, mock_db):
        """Testa erro de banco de dados."""
        mock_comment = Mock()
        mock_comment.status.value = "pending"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment
        mock_db.commit.side_effect = SQLAlchemyError("DB Error")

        update_data = schemas.CommentUpdateStatus(status="approved")

        with pytest.raises(CommentUpdateException):
            update_comment_status(mock_db, 1, update_data)


class TestDeleteComment:
    """Testes para delete_comment."""

    def test_delete_comment_success(self, mock_db):
        """Testa exclusão bem-sucedida."""
        mock_comment = Mock()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        result = delete_comment(mock_db, 1, True)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_comment)
        mock_db.commit.assert_called_once()

    def test_delete_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(CommentNotFoundException):
            delete_comment(mock_db, 1, True)

    def test_delete_comment_no_permission(self, mock_db):
        """Testa falta de permissão."""
        with pytest.raises(CommentPermissionDeniedException):
            delete_comment(mock_db, 1, False)

    def test_delete_comment_db_error(self, mock_db):
        """Testa erro de banco de dados."""
        mock_comment = Mock()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment
        mock_db.commit.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(CommentDeleteException):
            delete_comment(mock_db, 1, True)


class TestGetAllCommentsByLocationId:
    """Testes para get_all_comments_by_location_id."""

    def test_get_comments_by_location_success(self, mock_db):
        """Testa obtenção bem-sucedida de comentários por localização."""
        mock_comments = [Mock(), Mock()]
        mock_comments[0].images = None
        mock_comments[1].images = ["image.jpg"]

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_comments
        )

        result = get_all_comments_by_location_id(1, 0, 10, mock_db)

        assert result == mock_comments
        assert mock_comments[0].images == []
        assert mock_comments[1].images == ["image.jpg"]

    def test_get_comments_by_location_empty(self, mock_db):
        """Testa lista vazia."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = get_all_comments_by_location_id(1, 0, 10, mock_db)

        assert result == []

    def test_get_comments_by_location_error(self, mock_db):
        """Testa erro genérico."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.side_effect = Exception(
            "DB Error"
        )

        with pytest.raises(CommentGenericException):
            get_all_comments_by_location_id(1, 0, 10, mock_db)
