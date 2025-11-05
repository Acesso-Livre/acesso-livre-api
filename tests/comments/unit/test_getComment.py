from unittest.mock import MagicMock

import pytest

from acesso_livre_api.src.comments import exceptions, service


def test_get_comment_with_status_pending_success():
    db_mock = MagicMock()
    
    db_mock.query().filter().all.return_value = [
        MagicMock(
            id=1,
            user_name="test_user",
            rating=5,
            comment="Great place!",
            location_id=123,
            status="pending",
            images=["image1.jpg", "image2.jpg"],
            created_at="2024-01-01T12:00:00Z"
        ),
        MagicMock(
            id=2,
            user_name="another_user",
            rating=4,
            comment="Nice ambiance.",   
            location_id=456,
            status="pending",
            images=[],
            created_at="2024-01-02T15:30:00Z"
        )
    ]

    comments = service.get_comments_with_status_pending(db_mock)

    assert len(comments) == 2
    assert comments[0].id == 1
    assert comments[0].status == "pending"
    assert comments[1].id == 2
    assert comments[1].status == "pending"
    
def test_get_comment_with_id():
    db_mock = MagicMock()
    comment_id = 1
    expected_comment = MagicMock(
        id=comment_id,
        user_name="test_user",
        rating=5,
        comment="Great place!",
        images=["image1.jpg", "image2.jpg"],
        created_at="2024-01-01T12:00:00Z"
    )
    db_mock.query().filter().first.return_value = expected_comment

    comment = service.get_comment(db_mock, comment_id)

    assert comment.id == expected_comment.id
    assert comment.user_name == expected_comment.user_name
    assert comment.rating == expected_comment.rating
    assert comment.comment == expected_comment.comment
    assert comment.images == expected_comment.images
    assert comment.created_at == expected_comment.created_at

def test_get_comment_not_found():
    db_mock = MagicMock()
    comment_id = 999
    db_mock.query().filter().first.return_value = None

    with pytest.raises(exceptions.CommentNotFoundException):
        service.get_comment(db_mock, comment_id)

def test_get_comment_generic_exception():
    db_mock = MagicMock()
    comment_id = 1
    db_mock.query().filter().first.side_effect = Exception("Database error")

    with pytest.raises(exceptions.CommentNotFoundException):
        service.get_comment(db_mock, comment_id)

def test_get_comment_images_none():
    db_mock = MagicMock()
    comment_id = 1
    expected_comment = MagicMock(
        id=comment_id,
        user_name="test_user",
        rating=5,
        comment="Great place!",
        images=None,
        created_at="2024-01-01T12:00:00Z"
    )
    db_mock.query().filter().first.return_value = expected_comment

    comment = service.get_comment(db_mock, comment_id)

    assert comment.id == expected_comment.id
    assert comment.images == []  # Verifica se as imagens foram definidas como lista vazia
    assert comment.user_name == expected_comment.user_name
    assert comment.rating == expected_comment.rating
    assert comment.comment == expected_comment.comment
    assert comment.created_at == expected_comment.created_at