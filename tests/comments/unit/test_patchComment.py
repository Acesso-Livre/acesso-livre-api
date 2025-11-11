from unittest.mock import MagicMock

import pytest

from acesso_livre_api.src.comments import schemas, service
from acesso_livre_api.src.comments.models import CommentStatus


def test_patch_comment_success():
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

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)
    updated_comment = service.update_comment_status(
        db_mock, comment_id=1, new_status=new_status
    )

    assert updated_comment.status == CommentStatus.APPROVED
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


def test_patch_comment_status_invalid():
    db_mock = MagicMock()

    new_status = MagicMock()
    new_status.status = MagicMock(value="invalid_status")

    db_mock.query().filter().first.return_value = None

    with pytest.raises(service.CommentStatusInvalidException):
        service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


def test_patch_comment_not_found():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.APPROVED)

    with pytest.raises(service.CommentNotFoundException):
        service.update_comment_status(db_mock, comment_id=999, new_status=new_status)


def test_patch_comment_not_pending():
    db_mock = MagicMock()

    # Simulate a comment that is not pending
    existing_comment = MagicMock(id=1, status=CommentStatus.APPROVED)
    db_mock.query().filter().first.return_value = existing_comment

    new_status = schemas.CommentUpdateStatus(status=CommentStatus.REJECTED)

    with pytest.raises(service.CommentNotPendingException):
        service.update_comment_status(db_mock, comment_id=1, new_status=new_status)


def test_patch_comments_with_generic_exception():
    db_mock = MagicMock()
    db_mock.query().filter().order_by().offset().limit().all.side_effect = Exception(
        "Database error"
    )

    with pytest.raises(service.CommentGenericException):
        service.get_comments_with_status_pending(db_mock)


def test_patch_comment_with_update_error():
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
        service.update_comment_status(db_mock, comment_id=1, new_status=new_status)
