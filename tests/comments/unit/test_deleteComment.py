from unittest.mock import MagicMock, AsyncMock

import pytest

from acesso_livre_api.src.comments import service, exceptions
from acesso_livre_api.src.comments.models import CommentStatus


@pytest.mark.asyncio
async def test_delete_comment_success():
    db_mock = AsyncMock()

    # create a comment to be deleted
    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=["image1.jpg"],
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    await service.delete_comment(db_mock, comment_id=1)

    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_not_found():
    db_mock = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(exceptions.CommentNotFoundException):
        await service.delete_comment(db_mock, comment_id=999)


@pytest.mark.asyncio
async def test_delete_comment_permission_denied():
    db_mock = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock(
        id=1
    )  # Mock the comment lookup
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(exceptions.CommentPermissionDeniedException):
        await service.delete_comment(db_mock, comment_id=1, user_permissions=False)


@pytest.mark.asyncio
async def test_delete_comment_db_error():
    db_mock = AsyncMock()

    # create a comment to be deleted
    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=["image1.jpg"],
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)
    db_mock.commit.side_effect = Exception("DB error")

    db_mock.rollback = AsyncMock()

    with pytest.raises(exceptions.CommentDeleteException):
        await service.delete_comment(db_mock, comment_id=1)

    db_mock.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_generic_exception():
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=Exception("Generic error"))

    # Mock do rollback para evitar erro de método não aguardado
    db_mock.rollback = AsyncMock()

    with pytest.raises(exceptions.CommentDeleteException):
        await service.delete_comment(db_mock, comment_id=1)

    db_mock.rollback.assert_awaited_once()
