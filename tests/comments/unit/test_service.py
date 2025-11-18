from unittest.mock import Mock, MagicMock, AsyncMock, patch

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

    @pytest.mark.asyncio
    async def test_create_comment_success(self, mock_db, sample_comment_data):
        """Testa criação bem-sucedida de comentário."""
        mock_comment = Mock()
        mock_comment.id = 1
        mock_comment.status = "pending"

        with (
            patch(
                "acesso_livre_api.src.comments.service.models.Comment"
            ) as mock_comment_class,
            patch("acesso_livre_api.src.comments.service.datetime") as mock_datetime,
        ):

            mock_comment_class.return_value = mock_comment
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = await create_comment(mock_db, sample_comment_data)

            assert result == mock_comment
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_comment_rating_invalid(self, mock_db):
        """Testa erro de avaliação inválida."""
        mock_comment_data = Mock()
        mock_comment_data.rating = 6
        with pytest.raises(CommentRatingInvalidException):
            await create_comment(mock_db, mock_comment_data)

    @pytest.mark.asyncio
    async def test_create_comment_db_error(self, mock_db, sample_comment_data):
        """Testa erro de banco de dados."""
        with (
            patch("acesso_livre_api.src.comments.service.models.Comment"),
            patch("acesso_livre_api.src.comments.service.datetime"),
        ):

            mock_db.commit.side_effect = SQLAlchemyError("DB Error")

            with pytest.raises(CommentCreateException):
                await create_comment(mock_db, sample_comment_data)


class TestGetComment:
    """Testes para get_comment."""

    @pytest.mark.asyncio
    async def test_get_comment_success(self, mock_db):
        """Testa obtenção bem-sucedida de comentário."""
        mock_comment = Mock()
        mock_comment.images = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        result = await get_comment(mock_db, 1)

        assert result == mock_comment
        assert mock_comment.images == []

    @pytest.mark.asyncio
    async def test_get_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(CommentNotFoundException):
            await get_comment(mock_db, 1)

    @pytest.mark.asyncio
    async def test_get_comment_generic_error(self, mock_db):
        """Testa erro genérico."""
        mock_db.query.side_effect = Exception("Generic error")

        with pytest.raises(CommentNotFoundException):
            await get_comment(mock_db, 1)


class TestGetCommentsWithStatusPending:
    """Testes para get_comments_with_status_pending."""

    @pytest.mark.asyncio
    @patch(
        "acesso_livre_api.src.comments.service.get_signed_urls", new_callable=AsyncMock
    )
    async def test_get_comments_pending_success(self, mock_get_signed_urls, mock_db):
        """Testa obtenção bem-sucedida de comentários pendentes."""
        mock_get_signed_urls.return_value = ["image.jpg"]

        mock_comment1 = MagicMock()
        mock_comment1.images = None

        mock_comment2 = MagicMock()
        mock_comment2.images = ["image.jpg"]

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        result = await get_comments_with_status_pending(mock_db, skip=0, limit=10)

        assert result == [mock_comment1, mock_comment2]
        assert result[0].images == []
        assert result[1].images == ["image.jpg"]

    @pytest.mark.asyncio
    async def test_get_comments_pending_empty(self, mock_db):
        """Testa lista vazia de comentários pendentes."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = await get_comments_with_status_pending(mock_db, skip=0, limit=10)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_comments_pending_error(self, mock_db):
        """Testa erro ao buscar comentários pendentes."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.side_effect = Exception(
            "DB Error"
        )

        with pytest.raises(CommentGenericException):
            await get_comments_with_status_pending(mock_db, skip=0, limit=10)


class TestUpdateCommentStatus:
    """Testes para update_comment_status."""

    @pytest.mark.asyncio
    @patch("acesso_livre_api.src.comments.service.update_location_average_rating")
    async def test_update_comment_status_success(self, mock_update_avg, mock_db):
        """Testa atualização bem-sucedida de status."""
        mock_comment = Mock()
        mock_comment.status = "pending"
        mock_comment.images = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        update_data = schemas.CommentUpdateStatus(status="approved")

        result = await update_comment_status(mock_db, 1, update_data)

        assert result == mock_comment
        assert mock_comment.status == "approved"
        assert mock_comment.images == []
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_comment_status_invalid_status(self, mock_db):
        """Testa status inválido."""
        mock_update_data = Mock()
        mock_update_data.status.value = "invalid_status"

        with pytest.raises(CommentStatusInvalidException):
            await update_comment_status(mock_db, 1, mock_update_data)

    @pytest.mark.asyncio
    async def test_update_comment_status_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        update_data = schemas.CommentUpdateStatus(status="approved")

        with pytest.raises(CommentNotFoundException):
            await update_comment_status(mock_db, 1, update_data)

    @pytest.mark.asyncio
    async def test_update_comment_status_not_pending(self, mock_db):
        """Testa comentário que não está pendente."""
        mock_comment = Mock()
        mock_comment.status = "approved"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        update_data = schemas.CommentUpdateStatus(status="rejected")

        with pytest.raises(CommentNotPendingException):
            await update_comment_status(mock_db, 1, update_data)

    @pytest.mark.asyncio
    async def test_update_comment_status_db_error(self, mock_db):
        """Testa erro de banco de dados."""
        mock_comment = Mock()
        mock_comment.status = "pending"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment
        mock_db.commit.side_effect = SQLAlchemyError("DB Error")

        update_data = schemas.CommentUpdateStatus(status="approved")

        with pytest.raises(CommentUpdateException):
            await update_comment_status(mock_db, 1, update_data)


class TestDeleteComment:
    """Testes para delete_comment."""

    @pytest.mark.asyncio
    async def test_delete_comment_success(self, mock_db):
        """Testa exclusão bem-sucedida."""
        mock_comment = Mock()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

        result = await delete_comment(mock_db, 1, True)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_comment)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(CommentNotFoundException):
            await delete_comment(mock_db, 1, True)

    @pytest.mark.asyncio
    async def test_delete_comment_no_permission(self, mock_db):
        """Testa falta de permissão."""
        with pytest.raises(CommentPermissionDeniedException):
            await delete_comment(mock_db, 1, False)

    @pytest.mark.asyncio
    async def test_delete_comment_db_error(self, mock_db):
        """Testa erro de banco de dados."""
        mock_comment = Mock()

        mock_db.query.return_value.filter.return_value.first.return_value = mock_comment
        mock_db.commit.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(CommentDeleteException):
            await delete_comment(mock_db, 1, True)


class TestGetAllCommentsByLocationId:
    """Testes para get_all_comments_by_location_id."""

    @pytest.mark.asyncio
    @patch(
        "acesso_livre_api.src.comments.service.get_signed_urls", new_callable=AsyncMock
    )
    async def test_get_comments_by_location_success(self, mock_get_signed_urls, mock_db):
        """Testa obtenção bem-sucedida de comentários por localização."""
        mock_get_signed_urls.return_value = ["image.jpg"]
        mock_comment1 = MagicMock()
        mock_comment1.images = None
        mock_comment2 = MagicMock()
        mock_comment2.images = ["image.jpg"]

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        result = await get_all_comments_by_location_id(1, 0, 10, mock_db)

        assert result == [mock_comment1, mock_comment2]
        assert result[0].images == []
        assert result[1].images == ["image.jpg"]

    @pytest.mark.asyncio
    async def test_get_comments_by_location_empty(self, mock_db):
        """Testa lista vazia."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = await get_all_comments_by_location_id(1, 0, 10, mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_comments_by_location_error(self, mock_db):
        """Testa erro genérico."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.side_effect = Exception(
            "DB Error"
        )

        with pytest.raises(CommentGenericException):
            await get_all_comments_by_location_id(1, 0, 10, mock_db)
