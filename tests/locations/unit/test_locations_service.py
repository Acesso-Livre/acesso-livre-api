from unittest.mock import MagicMock, AsyncMock

import pytest

from acesso_livre_api.src.locations.service import update_location_average_rating


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
