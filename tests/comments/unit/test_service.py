from unittest.mock import Mock, MagicMock, AsyncMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from acesso_livre_api.src.comments import schemas, models
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
    get_all_comments_with_accessibility_items,
    get_comment,
    get_comments_with_status_pending,
    update_comment_status,
)


@pytest.fixture
def mock_db():
    """Mock do banco de dados como AsyncSession-like."""
    m = AsyncMock()
    m.add = Mock()
    m.delete = AsyncMock()
    m.commit = AsyncMock()
    m.refresh = AsyncMock()
    m.rollback = AsyncMock()
    m.execute = AsyncMock()
    return m


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
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once()

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
    @patch("acesso_livre_api.src.comments.service.get_signed_urls")
    async def test_get_comment_success(self, mock_get_signed_urls, mock_db):
        """Testa obtenção bem-sucedida de comentário."""
        mock_get_signed_urls.return_value = []
        mock_comment = Mock()
        mock_comment.images = None
        mock_comment.icon_url = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_comment
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_comment(mock_db, 1)

        assert result == mock_comment
        assert mock_comment.images == []


    @pytest.mark.asyncio
    async def test_get_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(CommentNotFoundException):
            await get_comment(mock_db, 1)

    @pytest.mark.asyncio
    async def test_get_comment_generic_error(self, mock_db):
        """Testa erro genérico."""
        mock_db.execute = AsyncMock(side_effect=Exception("Generic error"))

        with pytest.raises(CommentNotFoundException):
            await get_comment(mock_db, 1)


class TestDeleteComment:
    """Testes para delete_comment."""

    @pytest.mark.asyncio
    async def test_delete_comment_success(self, mock_db):
        """Testa exclusão bem-sucedida."""
        mock_comment = Mock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_comment
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await delete_comment(mock_db, 1, True)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_comment)
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(self, mock_db):
        """Testa comentário não encontrado."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

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

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_comment
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        with pytest.raises(CommentDeleteException):
            await delete_comment(mock_db, 1, True)


class TestGetAllCommentsWithAccessibilityItems:
    """Testes para get_all_comments_with_accessibility_items."""

    @pytest.mark.asyncio
    async def test_get_comments_with_accessibility_items_success(self, mock_db):
        """Testa busca de comentários com itens de acessibilidade."""
        mock_comment = Mock()
        mock_comment.images = []

        mock_item = Mock()
        mock_item.id = 1
        mock_item.name = "Bebedouro"
        mock_item.icon_url = "icons/bebedouro.png"

        mock_location = Mock()
        mock_location.accessibility_items = [mock_item]

        # Mock para busca de comentários
        mock_comments_result = MagicMock()
        mock_comments_scalars = MagicMock()
        mock_comments_scalars.all.return_value = [mock_comment]
        mock_comments_result.scalars.return_value = mock_comments_scalars

        # Mock para busca de localização
        mock_location_result = MagicMock()
        mock_location_unique = MagicMock()
        mock_location_unique.scalar_one_or_none.return_value = mock_location
        mock_location_result.unique.return_value = mock_location_unique

        mock_db.execute = AsyncMock(
            side_effect=[mock_comments_result, mock_location_result]
        )

        with patch(
            "acesso_livre_api.src.comments.service.get_signed_urls",
            new_callable=AsyncMock,
        ) as mock_get_signed_urls:
            mock_get_signed_urls.return_value = ["https://signed-url.com/icons/bebedouro.png"]

            comments, accessibility_items = await get_all_comments_with_accessibility_items(
                location_id=1, skip=0, limit=10, db=mock_db
            )

            assert len(comments) == 1
            assert len(accessibility_items) == 1
            assert accessibility_items[0]["name"] == "Bebedouro"

    @pytest.mark.asyncio
    @patch("acesso_livre_api.src.comments.service.get_signed_urls", new_callable=AsyncMock)
    async def test_get_comments_with_accessibility_items_no_items(self, mock_get_signed_urls, mock_db):
        """Testa busca de comentários sem itens de acessibilidade."""
        mock_get_signed_urls.return_value = []
        mock_comment = Mock()
        mock_comment.images = []

        mock_location = Mock()
        mock_location.accessibility_items = []

        # Mock para busca de comentários
        mock_comments_result = MagicMock()
        mock_comments_scalars = MagicMock()
        mock_comments_scalars.all.return_value = [mock_comment]
        mock_comments_result.scalars.return_value = mock_comments_scalars

        # Mock para busca de localização
        mock_location_result = MagicMock()
        mock_location_unique = MagicMock()
        mock_location_unique.scalar_one_or_none.return_value = mock_location
        mock_location_result.unique.return_value = mock_location_unique

        mock_db.execute = AsyncMock(
            side_effect=[mock_comments_result, mock_location_result]
        )

        comments, accessibility_items = await get_all_comments_with_accessibility_items(
            location_id=1, skip=0, limit=10, db=mock_db
        )

        assert len(comments) == 1
        assert len(accessibility_items) == 0


    @pytest.mark.asyncio
    async def test_get_comments_with_accessibility_items_error(self, mock_db):
        """Testa erro ao buscar comentários com itens de acessibilidade."""
        mock_db.execute = AsyncMock(side_effect=Exception("DB Error"))

        with pytest.raises(CommentGenericException):
            await get_all_comments_with_accessibility_items(
                location_id=1, skip=0, limit=10, db=mock_db
            )
