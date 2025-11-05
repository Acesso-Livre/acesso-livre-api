

from unittest.mock import MagicMock

import pytest

from acesso_livre_api.src.comments import service
from acesso_livre_api.src.comments.models import CommentStatus


def test_delete_comment_success():
    db_mock = MagicMock()
    
    # create a comment to be deleted
    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=["image1.jpg"]
    )
    db_mock.query().filter().first.return_value = existing_comment

    service.delete_comment(db_mock, comment_id=1)

    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_called_once()

def test_delete_comment_not_found():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    with pytest.raises(service.CommentNotFoundException):
        service.delete_comment(db_mock, comment_id=999)

def test_delete_comment_permission_denied():
    db_mock = MagicMock()
    
    with pytest.raises(service.CommentPermissionDeniedException):
        service.delete_comment(db_mock, comment_id=1, user_permissions=False)

def test_delete_comment_db_error():
    db_mock = MagicMock()
    
    # create a comment to be deleted
    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=["image1.jpg"]
    )
    db_mock.query().filter().first.return_value = existing_comment
    db_mock.delete.side_effect = Exception("DB error")

    with pytest.raises(service.CommentDeleteException):
        service.delete_comment(db_mock, comment_id=1)

def test_delete_comment_generic_exception():
    db_mock = MagicMock()
    db_mock.query().filter().first.side_effect = Exception("Generic error")
    with pytest.raises(service.CommentDeleteException):
        service.delete_comment(db_mock, comment_id=1)