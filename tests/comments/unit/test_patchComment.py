from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from acesso_livre_api.src.comments import schemas, service, exceptions
from acesso_livre_api.src.comments.models import CommentStatus


@pytest.mark.asyncio
@patch(
    "acesso_livre_api.src.comments.service.update_location_average_rating",
    new_callable=AsyncMock,
)
async def test_patch_comment_success(mock_update_avg):
    db_mock = AsyncMock()

    original_comment = MagicMock(status=CommentStatus.PENDING, location_id=1, rating=4)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = original_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)
    updated_comment = await service.update_comment_status(
        db_mock, comment_id=1, new_status=new_status
    )

    assert updated_comment.status == CommentStatus.APPROVED
    db_mock.commit.assert_awaited_once()
    mock_update_avg.assert_awaited_once_with(db_mock, 1, 4)


@pytest.mark.asyncio
async def test_patch_comment_status_invalid():
    db_mock = AsyncMock()

    mock_comment = MagicMock(status=CommentStatus.PENDING)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    new_status = MagicMock()
    new_status.status = MagicMock()
    new_status.status.value = "invalid_status"

    with pytest.raises(exceptions.CommentStatusInvalidException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


@pytest.mark.asyncio
async def test_patch_comment_not_found():
    db_mock = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)

    with pytest.raises(exceptions.CommentNotFoundException):
        await service.update_comment_status(
            db_mock, comment_id=999, new_status=new_status
        )


@pytest.mark.asyncio
async def test_patch_comment_not_pending():
    db_mock = AsyncMock()

    existing_comment = MagicMock(id=1, status=CommentStatus.APPROVED)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.REJECTED)

    with pytest.raises(exceptions.CommentNotPendingException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


@pytest.mark.asyncio
@patch(
    "acesso_livre_api.src.comments.service.update_location_average_rating",
    new_callable=AsyncMock,
)
async def test_patch_comments_with_generic_exception(mock_update_avg):
    db_mock = AsyncMock()

    existing_comment = MagicMock(status=CommentStatus.PENDING)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    db_mock.commit = AsyncMock(side_effect=Exception("Database error"))

    db_mock.rollback = AsyncMock()

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)

    with pytest.raises(exceptions.CommentUpdateException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)

    db_mock.rollback.assert_awaited_once()
