from unittest.mock import MagicMock, AsyncMock

import pytest

from acesso_livre_api.src.comments import exceptions, service
from acesso_livre_api.src.comments.schemas import CommentCreate


@pytest.mark.asyncio
async def test_create_comment_success():
    db_mock = AsyncMock()

    # Mock para simular que a localização existe
    mock_location_result = AsyncMock()
    mock_location_result.scalar_one_or_none.return_value = MagicMock(id=123)
    db_mock.execute.return_value = mock_location_result

    commentToUp = CommentCreate(
        user_name="Maria Silva", rating=4, comment="mocked comment", location_id=123
    )
    comment = await service.create_comment(db_mock, commentToUp)

    assert comment is not None

    db_mock.add.assert_called_once()
    db_mock.commit.assert_awaited_once()
    db_mock.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_comment_with_invalid_rating():
    db_mock = AsyncMock()
    # Usamos model_construct para contornar a validação do Pydantic e testar a verificação do próprio serviço.
    invalid_comment = CommentCreate.model_construct(
        user_name="Maria Silva", rating=6, comment="Ótimo lugar!", location_id=1
    )
    with pytest.raises(exceptions.CommentRatingInvalidException):
        await service.create_comment(db_mock, invalid_comment)


@pytest.mark.asyncio
async def test_create_comment_internal_error():
    db_mock = AsyncMock()
    db_mock.commit.side_effect = Exception("Database error")

    # Mock para simular que a localização existe
    mock_location_result = AsyncMock()
    mock_location_result.scalar_one_or_none.return_value = MagicMock(id=123)
    db_mock.execute.return_value = mock_location_result

    commentToUp = CommentCreate(
        user_name="Ana Pereira", rating=5, comment="mocked comment", location_id=123
    )

    with pytest.raises(exceptions.CommentCreateException):
        await service.create_comment(db_mock, commentToUp)

    db_mock.rollback.assert_awaited_once()
