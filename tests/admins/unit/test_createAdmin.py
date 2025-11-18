from unittest.mock import MagicMock, AsyncMock

import pytest
from pydantic import ValidationError

from acesso_livre_api.src.admins import exceptions, service
from acesso_livre_api.src.admins.schemas import AdminCreate


@pytest.mark.asyncio
async def test_create_admin_email_exists():
    # Mock da sessão do banco de dados
    db_mock = AsyncMock()

    # Mock do resultado da query - email já existe
    mock_admin = MagicMock()
    mock_admin.email = "validadmin@gmail.com"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    # Criar um admin com email que já existe
    admin = AdminCreate(email="validadmin@gmail.com", password="ValidPass123!")

    # Verificar se a exceção correta é levantada
    with pytest.raises(exceptions.AdminAlreadyExistsException):
        await service.create_admin(db_mock, admin)


@pytest.mark.asyncio
async def test_create_admin_success():
    db_mock = AsyncMock()

    # Mock do resultado da query - email não existe
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    admin = AdminCreate(email="validadmin@gmail.com", password="ValidPass123!")

    result = await service.create_admin(db_mock, admin)
    assert result is True
    db_mock.add.assert_called_once()
    db_mock.commit.assert_awaited_once()
    db_mock.refresh.assert_awaited_once()


def test_create_admin_weak_password():
    # A exceção agora é levantada pelo Pydantic na criação do schema
    with pytest.raises(exceptions.AdminWeakPasswordException):
        AdminCreate(email="validadmin@gmail.com", password="invalidpass!")


def test_create_admin_invalid_email():
    with pytest.raises(exceptions.AdminInvalidEmailException):
        AdminCreate(email="usuario!invalido@dominio.com", password="ValidPass123!")


def test_create_admin_empty_email():
    with pytest.raises(ValidationError):
        AdminCreate(email="", password="ValidPass123!")


def test_create_admin_empty_password():
    with pytest.raises(ValidationError):
        AdminCreate(email="validadmin@gmail.com", password="")


@pytest.mark.asyncio
async def test_create_admin_general_exception():
    # Mock da sessão do banco de dados
    db_mock = AsyncMock()

    # Mock do resultado da query - email não existe
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    # Simular uma exceção genérica ao commitar o admin
    db_mock.commit = AsyncMock(side_effect=Exception("Database error"))

    # Mock do rollback para evitar erro de método não aguardado
    db_mock.rollback = AsyncMock()

    admin = AdminCreate(email="validadmin@gmail.com", password="ValidPass123!")

    with pytest.raises(exceptions.AdminCreationException):
        await service.create_admin(db_mock, admin)
    db_mock.add.assert_called_once()
    db_mock.rollback.assert_awaited_once()
    db_mock.commit.assert_awaited_once()
    db_mock.refresh.assert_not_called()
