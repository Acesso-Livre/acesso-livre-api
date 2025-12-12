"""Testes para remoção de imagens ao deletar localização."""

from unittest.mock import Mock, AsyncMock, MagicMock, patch
import pytest
from acesso_livre_api.src.locations import models
from acesso_livre_api.src.locations.service import delete_location

@pytest.fixture
def mock_db():
    """Mock do banco de dados como AsyncSession-like."""
    m = AsyncMock()
    m.execute = AsyncMock()
    m.delete = AsyncMock()
    m.commit = AsyncMock()
    m.rollback = AsyncMock()
    return m

@pytest.fixture
def mock_location():
    """Mock de uma localização."""
    location = Mock(spec=models.Location)
    location.id = 1
    location.images = ["image1.jpg", "image2.jpg"]
    return location

class TestDeleteLocationImages:
    """Testes para delete_location com remoção de imagens."""

    @pytest.mark.asyncio
    async def test_delete_location_with_images(self, mock_db, mock_location):
        """Testa se as imagens são deletadas ao excluir a localização."""
        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_location
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("acesso_livre_api.src.locations.service.delete_images") as mock_delete_images:
            mock_delete_images.return_value = True

            result = await delete_location(mock_db, location_id=1)

            assert result is True
            mock_delete_images.assert_awaited_once_with(["image1.jpg", "image2.jpg"])
            mock_db.delete.assert_awaited_once_with(mock_location)
            mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_location_without_images(self, mock_db, mock_location):
        """Testa exclusão de localização sem imagens."""
        mock_location.images = []
        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_location
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("acesso_livre_api.src.locations.service.delete_images") as mock_delete_images:
            result = await delete_location(mock_db, location_id=1)

            assert result is True
            mock_delete_images.assert_not_called()
            mock_db.delete.assert_awaited_once_with(mock_location)
            mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_location_image_deletion_failure(self, mock_db, mock_location):
        """Testa se a exclusão da localização prossegue mesmo se a deleção de imagens falhar."""
        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_location
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("acesso_livre_api.src.locations.service.delete_images") as mock_delete_images:
            mock_delete_images.side_effect = Exception("Storage error")

            result = await delete_location(mock_db, location_id=1)

            assert result is True
            mock_delete_images.assert_awaited_once()
            mock_db.delete.assert_awaited_once_with(mock_location)
            mock_db.commit.assert_awaited_once()