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


def test_get_all_comments_by_location_id_success():
    db_mock = MagicMock()
    location_id = 123
    skip = 0
    limit = 10

    db_mock.query().filter().offset().limit().all.return_value = [
        MagicMock(
            id=1,
            user_name="João Silva",
            rating=5,
            comment="Excelente local, muito acessível!",
            location_id=location_id,
            status="approved",
            images=["https://example.com/image1.jpg"],
            created_at="2023-10-01T12:00:00Z"
        ),
        MagicMock(
            id=2,
            user_name="Maria Santos",
            rating=4,
            comment="Bom local, mas poderia melhorar a sinalização.",
            location_id=location_id,
            status="pending",
            images=[],
            created_at="2023-10-02T14:30:00Z"
        )
    ]

    comments = service.get_all_comments_by_location_id(location_id, skip, limit, db_mock)

    assert len(comments) == 2
    assert comments[0].id == 1
    assert comments[0].user_name == "João Silva"
    assert comments[0].rating == 5
    assert comments[0].comment == "Excelente local, muito acessível!"
    assert comments[0].location_id == location_id
    assert comments[0].status == "approved"
    assert comments[0].images == ["https://example.com/image1.jpg"]
    assert comments[0].created_at == "2023-10-01T12:00:00Z"

    assert comments[1].id == 2
    assert comments[1].user_name == "Maria Santos"
    assert comments[1].rating == 4
    assert comments[1].comment == "Bom local, mas poderia melhorar a sinalização."
    assert comments[1].location_id == location_id
    assert comments[1].status == "pending"
    assert comments[1].images == []
    assert comments[1].created_at == "2023-10-02T14:30:00Z"


def test_get_all_comments_by_location_id_empty_list():
    db_mock = MagicMock()
    location_id = 123
    skip = 0
    limit = 10

    db_mock.query().filter().offset().limit().all.return_value = []

    comments = service.get_all_comments_by_location_id(location_id, skip, limit, db_mock)

    assert comments == []


def test_get_all_comments_by_location_id_with_pagination():
    db_mock = MagicMock()
    location_id = 123
    skip = 5
    limit = 3

    db_mock.query().filter().offset().limit().all.return_value = [
        MagicMock(
            id=6,
            user_name="User 6",
            rating=3,
            comment="Comment 6",
            location_id=location_id,
            status="approved",
            images=[],
            created_at="2023-10-06T12:00:00Z"
        )
    ]

    comments = service.get_all_comments_by_location_id(location_id, skip, limit, db_mock)

    assert len(comments) == 1
    assert comments[0].id == 6


def test_get_all_comments_by_location_id_generic_exception():
    db_mock = MagicMock()
    location_id = 123
    skip = 0
    limit = 10

    db_mock.query().filter().offset().limit().all.side_effect = Exception("Database error")

    with pytest.raises(exceptions.CommentGenericException):
        service.get_all_comments_by_location_id(location_id, skip, limit, db_mock)


def test_get_all_comments_by_location_id_images_none():
    db_mock = MagicMock()
    location_id = 123
    skip = 0
    limit = 10

    comment_mock = MagicMock(
        id=1,
        user_name="Test User",
        rating=5,
        comment="Test comment",
        location_id=location_id,
        status="approved",
        images=None,
        created_at="2023-10-01T12:00:00Z"
    )

    db_mock.query().filter().offset().limit().all.return_value = [comment_mock]

    comments = service.get_all_comments_by_location_id(location_id, skip, limit, db_mock)

    assert len(comments) == 1
    assert comments[0].images == []  # Verifica se as imagens foram definidas como lista vazia