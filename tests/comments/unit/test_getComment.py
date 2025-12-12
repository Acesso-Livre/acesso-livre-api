from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from acesso_livre_api.src.comments import exceptions, service, schemas


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.get_images_with_ids")
@patch("acesso_livre_api.src.comments.service.get_signed_urls")
async def test_get_comment_with_status_pending_success(mock_get_signed_urls, mock_get_images_with_ids):
    db_mock = AsyncMock()
    mock_get_images_with_ids.return_value = [
        schemas.ImageResponse(id="uuid1", url="signed_url_1"),
        schemas.ImageResponse(id="uuid2", url="signed_url_2")
    ]
    mock_get_signed_urls.return_value = ["signed_icon_url"]

    mock_comment_1 = MagicMock(images=["uuid1.jpg"], icon_url="icon1.jpg")
    mock_comment_2 = MagicMock(images=["uuid2.jpg"], icon_url=None)

    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = [mock_comment_1, mock_comment_2]
    db_mock.execute = AsyncMock(return_value=mock_result)

    comments = await service.get_comments_with_status_pending(db_mock, skip=0, limit=10)

    assert len(comments) == 2
    db_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.get_signed_urls")
async def test_get_comment_with_id(mock_get_signed_urls):
    db_mock = AsyncMock()
    comment_id = 1
    expected_comment = MagicMock(images=["image1.jpg"], status="approved", icon_url=None)
    mock_get_signed_urls.return_value = ["signed_url.jpg"]

    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.first.return_value = expected_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    comment = await service.get_comment(db_mock, comment_id)

    assert comment == expected_comment
    assert comment.images == ["signed_url.jpg"]
    mock_get_signed_urls.assert_called_once_with(["image1.jpg"])
    db_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comment_not_found():
    db_mock = AsyncMock()
    comment_id = 999

    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.first.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(exceptions.CommentNotFoundException):
        await service.get_comment(db_mock, comment_id)

    db_mock.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_comment_generic_exception():
    db_mock = AsyncMock()
    comment_id = 1
    db_mock.execute = AsyncMock(side_effect=Exception("Database error"))

    with pytest.raises(exceptions.CommentNotFoundException):
        await service.get_comment(db_mock, comment_id)


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.get_signed_urls")
async def test_get_comment_images_none(mock_get_signed_urls):
    db_mock = AsyncMock()
    comment_id = 1
    expected_comment = MagicMock(images=None, status="approved", icon_url=None)
    mock_get_signed_urls.return_value = []

    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.first.return_value = expected_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    comment = await service.get_comment(db_mock, comment_id)

    assert comment.images == []
    mock_get_signed_urls.assert_not_called()
    db_mock.execute.assert_awaited_once()

