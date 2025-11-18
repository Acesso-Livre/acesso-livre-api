from unittest.mock import MagicMock

import pytest

from acesso_livre_api.src.comments import exceptions, service
from acesso_livre_api.src.comments.schemas import CommentCreate


@pytest.mark.asyncio
async def test_create_comment_success():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(id=1, status="pending")
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    commentToUp = CommentCreate(
        user_name="Maria Silva", rating=4, comment="mocked comment", location_id=123
    )
    comment = await service.create_comment(db_mock, commentToUp)

    assert comment is not None

    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_comment_with_invalid_rating():
    db_mock = MagicMock()
    # Usamos model_construct para contornar a validação do Pydantic e testar a verificação do próprio serviço.
    invalid_comment = CommentCreate.model_construct(
        user_name="Maria Silva", rating=6, comment="Ótimo lugar!", location_id=1
    )
    with pytest.raises(exceptions.CommentRatingInvalidException):
        await service.create_comment(db_mock, invalid_comment)


@pytest.mark.asyncio
async def test_create_comment_internal_error():
    db_mock = MagicMock()
    db_mock.commit.side_effect = Exception("Database error")

    commentToUp = CommentCreate(
        user_name="Ana Pereira", rating=5, comment="mocked comment", location_id=123
    )

    with pytest.raises(exceptions.CommentCreateException):
        await service.create_comment(db_mock, commentToUp)

    db_mock.rollback.assert_called_once()
