from unittest.mock import MagicMock, patch

import pytest

from acesso_livre_api.src.comments import schemas, service
from acesso_livre_api.src.comments.models import CommentStatus


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.update_location_average_rating")
async def test_patch_comment_success(mock_update_avg):
    db_mock = MagicMock()

    # create a comment to be updated without images
    original_comment = MagicMock(
        user_name="test_user",
        rating=3,
        comment="It's okay.",
        status=CommentStatus.PENDING,
        images=[],  # Sem imagens
    )
    db_mock.query().filter().first.return_value = original_comment

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)
    updated_comment = await service.update_comment_status(
        db_mock, comment_id=1, new_status=new_status
    )

    assert updated_comment.status == CommentStatus.APPROVED


@pytest.mark.asyncio
async def test_patch_comment_status_invalid():
    db_mock = MagicMock()

    new_status = MagicMock()
    new_status.status = MagicMock(value="invalid_status")

    db_mock.query().filter().first.return_value = None

    with pytest.raises(service.CommentStatusInvalidException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


@pytest.mark.asyncio
async def test_patch_comment_not_found():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)

    with pytest.raises(service.CommentNotFoundException):
        await service.update_comment_status(
            db_mock, comment_id=999, new_status=new_status
        )


@pytest.mark.asyncio
async def test_patch_comment_not_pending():
    db_mock = MagicMock()

    # Simulate a comment that is not pending
    existing_comment = MagicMock(id=1, status=CommentStatus.APPROVED)
    db_mock.query().filter().first.return_value = existing_comment

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.REJECTED)

    with pytest.raises(service.CommentNotPendingException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


@pytest.mark.asyncio
async def test_patch_comments_with_generic_exception():
    db_mock = MagicMock()

    existing_comment = MagicMock(id=1, status=CommentStatus.PENDING)
    db_mock.query().filter().first.return_value = existing_comment

    db_mock.commit.side_effect = Exception("Database error")

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)

    with pytest.raises(service.CommentUpdateException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


@pytest.mark.asyncio
async def test_patch_comment_with_update_error():
    db_mock = MagicMock()

    # create a comment to be updated
    original_comment = MagicMock(
        user_name="test_user",
        rating=3,
        comment="It's okay.",
        status=CommentStatus.PENDING,
        images=["old_image.jpg"],
    )
    db_mock.query().filter().first.return_value = original_comment
    db_mock.commit.side_effect = Exception("DB error")
    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)
    with pytest.raises(service.CommentUpdateException):
        await service.update_comment_status(db_mock, comment_id=1, new_status=new_status)
