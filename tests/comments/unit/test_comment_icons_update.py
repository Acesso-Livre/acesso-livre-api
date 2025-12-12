"""Testes para atualização de ícones de comentário."""

from unittest.mock import Mock, AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile

from acesso_livre_api.src.comments import models
from acesso_livre_api.src.comments.exceptions import CommentGenericException
from acesso_livre_api.src.comments.service import update_comment_icon


@pytest.fixture
def mock_db():
    """Mock do banco de dados como AsyncSession-like."""
    m = AsyncMock()
    m.execute = AsyncMock()
    m.commit = AsyncMock()
    m.refresh = AsyncMock()
    m.rollback = AsyncMock()
    return m


@pytest.fixture
def mock_comment_icon():
    """Mock de um ícone de comentário."""
    icon = Mock(spec=models.CommentIcon)
    icon.id = 1
    icon.name = "Feedback"
    icon.icon_url = "icons/feedback.png"
    return icon


class TestUpdateCommentIcon:
    """Testes para update_comment_icon."""

    @pytest.mark.asyncio
    async def test_update_comment_icon_name_only(self, mock_db, mock_comment_icon):
        """Testa atualização apenas do nome."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("acesso_livre_api.src.comments.service.get_signed_urls") as mock_get_urls:
            mock_get_urls.return_value = ["signed_url"]
            
            result = await update_comment_icon(
                mock_db, icon_id=1, name="Feedback Updated"
            )

            assert result.name == "Feedback Updated"
            assert result.icon_url == "signed_url"
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_comment_icon_image_only(self, mock_db, mock_comment_icon):
        """Testa atualização apenas da imagem, com remoção da antiga."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        mock_image = Mock(spec=UploadFile)

        with patch("acesso_livre_api.src.comments.service.upload_image.upload_image") as mock_upload, \
             patch("acesso_livre_api.src.comments.service.delete_image") as mock_delete, \
             patch("acesso_livre_api.src.comments.service.get_signed_urls") as mock_get_urls:
            
            mock_upload.return_value = "icons/new_feedback.png"
            mock_get_urls.return_value = ["signed_new_url"]
            
            result = await update_comment_icon(
                mock_db, icon_id=1, image=mock_image
            )

            assert result.icon_url == "signed_new_url"
            mock_upload.assert_awaited_once_with(mock_image)
            mock_delete.assert_awaited_once_with("icons/feedback.png")
            mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_comment_icon_full(self, mock_db, mock_comment_icon):
        """Testa atualização de nome e imagem."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        mock_image = Mock(spec=UploadFile)

        with patch("acesso_livre_api.src.comments.service.upload_image.upload_image") as mock_upload, \
             patch("acesso_livre_api.src.comments.service.delete_image") as mock_delete, \
             patch("acesso_livre_api.src.comments.service.get_signed_urls") as mock_get_urls:
            
            mock_upload.return_value = "icons/new_feedback.png"
            mock_get_urls.return_value = ["signed_new_url"]
            
            result = await update_comment_icon(
                mock_db, icon_id=1, name="Feedback Full Update", image=mock_image
            )

            assert result.name == "Feedback Full Update"
            assert result.icon_url == "signed_new_url"
            mock_upload.assert_awaited_once()
            mock_delete.assert_awaited_once()
            mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_comment_icon_not_found(self, mock_db):
        """Testa erro quando ícone não é encontrado."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(CommentGenericException):
            await update_comment_icon(mock_db, icon_id=999, name="Test")

    @pytest.mark.asyncio
    async def test_update_comment_icon_db_error(self, mock_db, mock_comment_icon):
        """Testa erro de banco de dados na atualização."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit.side_effect = SQLAlchemyError("DB Error")

        with pytest.raises(CommentGenericException):
            await update_comment_icon(mock_db, icon_id=1, name="Test")
        
        mock_db.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_comment_icon_delete_image_error(self, mock_db, mock_comment_icon):
        """Testa que erro na deleção de imagem não impede a atualização (apenas loga aviso)."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_comment_icon
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        mock_image = Mock(spec=UploadFile)

        with patch("acesso_livre_api.src.comments.service.upload_image.upload_image") as mock_upload, \
             patch("acesso_livre_api.src.comments.service.delete_image") as mock_delete, \
             patch("acesso_livre_api.src.comments.service.get_signed_urls") as mock_get_urls:
            
            mock_upload.return_value = "icons/new_feedback.png"
            mock_delete.side_effect = Exception("Delete Error")
            mock_get_urls.return_value = ["signed_new_url"]
            
            result = await update_comment_icon(
                mock_db, icon_id=1, image=mock_image
            )

            # Deve continuar com sucesso mesmo com erro na deleção
            assert result.icon_url == "signed_new_url"
            mock_upload.assert_awaited_once()
            mock_delete.assert_awaited_once()
            mock_db.commit.assert_awaited_once()