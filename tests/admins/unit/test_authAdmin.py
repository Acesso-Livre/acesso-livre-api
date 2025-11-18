from unittest.mock import MagicMock, AsyncMock
import pytest
from acesso_livre_api.src.admins import service, exceptions
from acesso_livre_api.src.admins.schemas import AdminCreate


@pytest.mark.asyncio
async def test_auth_admin_success():
    # Mock da sessão do banco de dados
    db_mock = AsyncMock()

    # Hash da senha correta
    hashedpassword = service.get_password_hash("ValidPass123!")

    # Mock do resultado da query
    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"
    mock_admin.password = hashedpassword

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    # Criar um admin
    admin = AdminCreate(email="validadmin@gmail.com", password="ValidPass123!")

    # Verificar se a autenticação é bem-sucedida
    result = await service.authenticate_admin(db_mock, admin.email, admin.password)
    assert result is not None
    assert result.email == admin.email
    assert result.password == hashedpassword


@pytest.mark.asyncio
async def test_auth_admin_invalid_email():
    db_mock = AsyncMock()

    # Mock do resultado da query - admin não encontrado
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    admin = AdminCreate(email="invalid@user.com", password="ValidPass123!")

    with pytest.raises(exceptions.AdminAuthenticationFailedException):
        await service.authenticate_admin(db_mock, admin.email, admin.password)


@pytest.mark.asyncio
async def test_auth_admin_invalid_password():
    db_mock = AsyncMock()

    hashedpassword = service.get_password_hash("ValidPass123!")

    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"
    mock_admin.password = hashedpassword

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    admin = AdminCreate(email="validadmin@gmail.com", password="WrongPass123!")

    with pytest.raises(exceptions.AdminAuthenticationFailedException):
        await service.authenticate_admin(db_mock, admin.email, admin.password)
