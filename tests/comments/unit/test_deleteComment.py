from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from acesso_livre_api.src.comments import service, exceptions
from acesso_livre_api.src.comments.models import CommentStatus


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_success(mock_delete_images):
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
    mock_result.scalars.return_value.first.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    await service.delete_comment(db_mock, comment_id=1)

    mock_delete_images.assert_awaited_once_with(["image1.jpg"])
    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_not_found():
    db_mock = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
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
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_db_error(mock_delete_images):
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
    mock_result.scalars.return_value.first.return_value = existing_comment
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


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_without_images(mock_delete_images):
    db_mock = AsyncMock()

    # create a comment to be deleted without images
    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=None,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    await service.delete_comment(db_mock, comment_id=1)

    mock_delete_images.assert_not_awaited()
    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_image_deletion_fails_but_comment_deleted(mock_delete_images):
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
    mock_result.scalars.return_value.first.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)
    mock_delete_images.side_effect = Exception("Image deletion failed")

    # A exclusão do comentário deve funcionar mesmo se a exclusão da imagem falhar
    await service.delete_comment(db_mock, comment_id=1)

    mock_delete_images.assert_awaited_once_with(["image1.jpg"])
    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()

@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_without_images(mock_delete_images):
    """Testa exclusão de comentário sem imagens."""
    db_mock = AsyncMock()

    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=None,  # Sem imagens
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    await service.delete_comment(db_mock, comment_id=1)

    # delete_images não deve ser chamado quando não há imagens
    mock_delete_images.assert_not_awaited()
    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
@patch("acesso_livre_api.src.comments.service.delete_images", new_callable=AsyncMock)
async def test_delete_comment_image_deletion_fails_but_comment_deleted(mock_delete_images):
    """Testa que o comentário é deletado mesmo quando a deleção de imagens falha."""
    db_mock = AsyncMock()
    mock_delete_images.side_effect = Exception("Storage error")

    existing_comment = MagicMock(
        id=1,
        user_name="test_user",
        rating=4,
        comment="Nice place.",
        status=CommentStatus.PENDING,
        images=["image1.jpg"],
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = existing_comment
    db_mock.execute = AsyncMock(return_value=mock_result)

    # Mesmo com erro ao deletar imagens, o comentário deve ser excluído
    await service.delete_comment(db_mock, comment_id=1)

    mock_delete_images.assert_awaited_once_with(["image1.jpg"])
    db_mock.delete.assert_called_once_with(existing_comment)
    db_mock.commit.assert_awaited_once()
