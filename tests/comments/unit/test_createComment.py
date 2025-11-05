

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from acesso_livre_api.src.comments import exceptions, service
from acesso_livre_api.src.comments.schemas import CommentCreate


def test_create_comment_success():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(id= 1,status= "pending")
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    commentToUp = CommentCreate(user_name="Maria Silva",rating= 4,comment= "mocked comment")
    comment = service.create_comment(db_mock, commentToUp)

    assert comment is not None

    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

def test_create_comment_with_invalid_rating():
    with pytest.raises(ValidationError):
        CommentCreate(user_name="Maria Silva", rating=6, comment="Ótimo lugar!")

def test_create_comment_with_invalid_images():
    db_mock = MagicMock()
    with pytest.raises(exceptions.CommentImagesInvalidException):
        comment = CommentCreate(user_name="João Souza", rating=4, comment="Lugar agradável.", images=[""])
        service.create_comment(db_mock, comment)


def test_create_comment_internal_error():
    db_mock = MagicMock()
    db_mock.commit.side_effect = Exception("Database error")

    commentToUp = CommentCreate(user_name="Ana Pereira",rating= 5,comment= "mocked comment")
    
    with pytest.raises(exceptions.CommentCreateException):
        service.create_comment(db_mock, commentToUp)

    db_mock.rollback.assert_called_once()