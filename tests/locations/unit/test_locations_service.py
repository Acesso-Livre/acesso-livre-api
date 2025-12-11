from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from acesso_livre_api.src.locations.service import update_location_average_rating, get_location_by_id
from acesso_livre_api.src.locations import schemas
from acesso_livre_api.src.comments.schemas import ImageResponse


@pytest.mark.asyncio
async def test_update_location_average_rating_first_comment():
    mock_db = AsyncMock()
    mock_location = MagicMock(avg_rating=None)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_location

    # Mock for the count query - return 1 approved comment (the one being added)
    mock_count_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [MagicMock()]  # 1 approved comment
    mock_count_result.scalars.return_value = mock_scalars

    # First execute returns the location, second returns the count result
    mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])

    await update_location_average_rating(mock_db, location_id=1, new_value=5.0)

    assert mock_location.avg_rating == 5.0
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_location)


@pytest.mark.asyncio
async def test_update_location_average_rating_additional_comment():
    mock_db = AsyncMock()
    mock_location = MagicMock(avg_rating=4.0)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_location

    # Mock para a contagem de comentários
    mock_count_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [MagicMock(), MagicMock()]  # 2 comentários aprovados
    mock_count_result.scalars.return_value = mock_scalars

    # O primeiro execute busca a localização, o segundo a contagem
    mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])

    await update_location_average_rating(mock_db, location_id=1, new_value=5.0)
    assert abs(mock_location.avg_rating - 4.5) < 0.001
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_location)


@pytest.mark.asyncio
async def test_update_location_average_rating_location_not_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    await update_location_average_rating(mock_db, location_id=999, new_value=5.0)

    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_update_location_average_rating_handling_none_avg():
    mock_db = AsyncMock()
    mock_location = MagicMock(avg_rating=None)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_location

    # Mock for the count query - return 1 approved comment (the one being added)
    mock_count_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [MagicMock()]  # 1 approved comment
    mock_count_result.scalars.return_value = mock_scalars

    # First execute returns the location, second returns the count result
    mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])

    await update_location_average_rating(mock_db, location_id=1, new_value=3.0)
    assert mock_location.avg_rating == 3.0
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_location)


@pytest.mark.asyncio
async def test_update_location_average_rating_db_error():
    mock_db = AsyncMock()
    mock_location = MagicMock(avg_rating=4.0)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_location
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock(side_effect=Exception("DB Error"))

    mock_db.rollback = AsyncMock()

    from acesso_livre_api.src.locations.exceptions import LocationUpdateException

    with pytest.raises(LocationUpdateException):
        await update_location_average_rating(mock_db, location_id=1, new_value=5.0)

    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_location_by_id_with_images():
    """Testa se get_location_by_id retorna imagens com ID usando ImageResponse."""
    mock_db = AsyncMock()
    
    # Mock location
    mock_location = MagicMock()
    mock_location.id = 1
    mock_location.name = "Shopping Center"
    mock_location.description = "Um shopping"
    mock_location.top = 45.2
    mock_location.left = 120.8
    mock_location.images = ["path/to/image1.png", "path/to/image2.png"]
    mock_location.avg_rating = 4.2
    mock_location.accessibility_items = []
    
    # Mock comment
    mock_comment = MagicMock()
    mock_comment.images = ["path/to/comment-image.png"]
    
    # Mock db responses - precisa retornar os resultados corretamente
    mock_location_result = MagicMock()
    mock_location_result.unique.return_value.scalar_one_or_none.return_value = mock_location
    
    mock_comments_result = MagicMock()
    mock_comments_result.scalars.return_value.all.return_value = [mock_comment]
    
    # Mock execute para retornar diferentes resultados
    async def mock_execute_side_effect(stmt):
        stmt_str = str(stmt).lower()
        if "locations" in stmt_str:
            return mock_location_result
        elif "comments" in stmt_str:
            return mock_comments_result
        return mock_location_result

    mock_db.execute = AsyncMock(side_effect=mock_execute_side_effect)
    mock_db.refresh = AsyncMock()
    
    # Mock get_images_with_ids
    mock_images_response = [
        ImageResponse(id="uuid1", url="https://example.com/image1.jpg"),
        ImageResponse(id="uuid2", url="https://example.com/image2.jpg"),
        ImageResponse(id="uuid3", url="https://example.com/comment-image.jpg"),
    ]
    
    with patch("acesso_livre_api.src.locations.service.get_images_with_ids", return_value=mock_images_response):
        with patch("acesso_livre_api.src.locations.service.get_signed_urls", return_value=[]):
            result = await get_location_by_id(mock_db, location_id=1)
    
    # Verificar se o resultado contém ImageResponse
    assert isinstance(result, schemas.LocationDetailResponse)
    assert len(result.images) == 3
    assert all(isinstance(img, ImageResponse) for img in result.images)
    assert result.images[0].id == "uuid1"
    assert result.images[0].url == "https://example.com/image1.jpg"


@pytest.mark.asyncio
async def test_get_location_by_id_no_images():
    """Testa se get_location_by_id retorna lista vazia quando não há imagens."""
    mock_db = AsyncMock()
    
    # Mock location sem imagens
    mock_location = MagicMock()
    mock_location.id = 1
    mock_location.name = "Local sem imagens"
    mock_location.description = "Um local sem imagens"
    mock_location.top = 10.0
    mock_location.left = 20.0
    mock_location.images = None
    mock_location.avg_rating = None
    mock_location.accessibility_items = []
    
    # Mock db responses
    mock_location_result = MagicMock()
    mock_location_result.unique.return_value.scalar_one_or_none.return_value = mock_location
    
    mock_comments_result = MagicMock()
    mock_comments_result.scalars.return_value.all.return_value = []
    
    # Mock execute para retornar diferentes resultados
    async def mock_execute_side_effect(stmt):
        stmt_str = str(stmt).lower()
        if "locations" in stmt_str:
            return mock_location_result
        elif "comments" in stmt_str:
            return mock_comments_result
        return mock_location_result

    mock_db.execute = AsyncMock(side_effect=mock_execute_side_effect)
    mock_db.refresh = AsyncMock()
    
    with patch("acesso_livre_api.src.locations.service.get_images_with_ids", return_value=[]):
        with patch("acesso_livre_api.src.locations.service.get_signed_urls", return_value=[]):
            result = await get_location_by_id(mock_db, location_id=1)
    
    assert isinstance(result, schemas.LocationDetailResponse)
    assert result.images == []
    assert result.avg_rating == 0.0
