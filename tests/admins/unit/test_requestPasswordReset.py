import pytest
from unittest.mock import AsyncMock, MagicMock
from acesso_livre_api.src.admins import exceptions, service


@pytest.mark.asyncio
async def test_request_password_reset_success():
    db_mock = AsyncMock()

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    result = await service.request_password_reset(db_mock, "validadmin@gmail.com")

    assert result is not None
    assert result == {"message": "Enviamos um link de recuperação ao email."}
    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_password_reset_admin_not_found():
    db_mock = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(exceptions.AdminNotFoundException):
        await service.request_password_reset(db_mock, "validadmin@gmail.com")


@pytest.mark.asyncio
async def test_request_password_reset_general_exception():
    db_mock = AsyncMock()
    db_mock.execute = AsyncMock(side_effect=Exception("DB error"))

    with pytest.raises(Exception):
        await service.request_password_reset(db_mock, "validadmin@gmail.com")
