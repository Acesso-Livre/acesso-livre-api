"""Testes para gerenciamento de ícones de comentário."""

from unittest.mock import Mock, AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError

from acesso_livre_api.src.comments import models, schemas
from acesso_livre_api.src.comments.exceptions import CommentGenericException
from acesso_livre_api.src.comments.service import (
    create_comment_icon,
    get_all_comment_icons,
    get_comment_icon_by_id,
    delete_comment_icon,
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
def mock_comment_icon():
    """Mock de um ícone de comentário."""
    icon = Mock(spec=models.CommentIcon)
    icon.id = 1
    icon.name = "Feedback"
    icon.icon_url = "icons/feedback.png"
    return icon


class TestCreateCommentIcon:
    """Testes para create_comment_icon."""

    @pytest.mark.asyncio
    async def test_create_comment_icon_success(self, mock_db, mock_comment_icon):
        """Testa criação bem-sucedida de ícone de comentário."""
        with patch("acesso_livre_api.src.comments.service.models.CommentIcon") as mock_class:
            mock_class.return_value = mock_comment_icon
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            result = await create_comment_icon(
                mock_db, name="Feedback", icon_url="icons/feedback.png"
            )

            assert result == mock_comment_icon
            mock_db.add.assert_called_once()
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_comment_icon_db_error(self, mock_db):
        """Testa erro de banco de dados na criação."""
        with patch("acesso_livre_api.src.comments.service.models.CommentIcon"):
            mock_db.commit.side_effect = SQLAlchemyError("DB Error")

            with pytest.raises(CommentGenericException):
                await create_comment_icon(
                    mock_db, name="Feedback", icon_url="icons/feedback.png"
                )

            mock_db.rollback.assert_awaited_once()


class TestGetAllCommentIcons:
    """Testes para get_all_comment_icons."""

    @pytest.mark.asyncio
    async def test_get_all_comment_icons_success(self, mock_db, mock_comment_icon):
        """Testa obtenção bem-sucedida de todos os ícones."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_comment_icon]
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "acesso_livre_api.src.comments.service.get_signed_urls"
        ) as mock_get_urls:
            mock_get_urls.return_value = ["signed_url"]
            
            result = await get_all_comment_icons(mock_db)

            assert len(result) == 1
            assert result[0] == mock_comment_icon
            mock_db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_comment_icons_empty(self, mock_db):
        """Testa obtenção quando não há ícones."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "acesso_livre_api.src.comments.service.get_signed_urls"
        ) as mock_get_urls:
            mock_get_urls.return_value = []
            
            result = await get_all_comment_icons(mock_db)

            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_comment_icons_error(self, mock_db):
        """Testa erro ao buscar ícones."""
        mock_db.execute.side_effect = Exception("Database error")

        with pytest.raises(CommentGenericException):
            await get_all_comment_icons(mock_db)


class TestGetCommentIconById:
    """Testes para get_comment_icon_by_id."""

    @pytest.mark.asyncio
    async def test_get_comment_icon_by_id_success(self, mock_db, mock_comment_icon):
        """Testa obtenção bem-sucedida de ícone por ID."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "acesso_livre_api.src.comments.service.get_signed_urls"
        ) as mock_get_urls:
            mock_get_urls.return_value = ["signed_url"]
            
            result = await get_comment_icon_by_id(mock_db, icon_id=1)

            assert result == mock_comment_icon
            mock_db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_comment_icon_by_id_not_found(self, mock_db):
        """Testa erro quando ícone não é encontrado."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(CommentGenericException):
            await get_comment_icon_by_id(mock_db, icon_id=999)


class TestDeleteCommentIcon:
    """Testes para delete_comment_icon."""

    @pytest.mark.asyncio
    async def test_delete_comment_icon_success(self, mock_db, mock_comment_icon):
        """Testa deleção bem-sucedida de ícone."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("acesso_livre_api.src.comments.service.delete_image") as mock_delete:
            mock_delete.return_value = None
            
            result = await delete_comment_icon(mock_db, icon_id=1)

            assert result is True
            mock_db.delete.assert_awaited_once()
            mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_comment_icon_not_found(self, mock_db):
        """Testa erro quando ícone não é encontrado."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(CommentGenericException):
            await delete_comment_icon(mock_db, icon_id=999)

    @pytest.mark.asyncio
    async def test_delete_comment_icon_db_error(self, mock_db, mock_comment_icon):
        """Testa erro de banco de dados na deleção."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        with patch("acesso_livre_api.src.comments.service.delete_image"):
            with pytest.raises(CommentGenericException):
                await delete_comment_icon(mock_db, icon_id=1)

            mock_db.rollback.assert_awaited_once()
