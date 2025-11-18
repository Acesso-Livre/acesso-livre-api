from unittest.mock import AsyncMock, MagicMock
import pytest
from datetime import datetime, timezone, timedelta

from acesso_livre_api.src import exceptions
from acesso_livre_api.src.admins import service
from acesso_livre_api.src.admins.exceptions import (
    AdminNotFoundException,
    InvalidResetTokenException,
    AdminWeakPasswordException,
)


@pytest.mark.asyncio
async def test_password_reset_success():
    # Mocks e Configuração Inicial
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Simular um token de reset valido, como se tivesse sido gerado antes
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(
        to_encode, service.settings.secret_key, algorithm=service.settings.algorithm
    )

    # Criar o mock do admin que sera "encontrado" no banco
    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.password = "old_hashed_password"
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    # Configurar o mock do DB para retornar o mock do admin
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    # Chamar a funcao a ser testada
    result = await service.password_reset(
        db=db_mock, code=code, email=email, new_password=new_password
    )

    # A senha do admin foi atualizada para o hash da nova senha?
    assert service.verify_password(new_password, mock_admin.password)

    # O token de reset foi invalidado?
    assert mock_admin.reset_token_hash is None
    assert mock_admin.reset_token_expires is None

    # As alteracoes foram salvas no banco?
    db_mock.commit.assert_awaited_once()

    # A funcao retornou a mensagem de sucesso?
    assert result == {"message": "Senha atualizada com sucesso!"}


@pytest.mark.asyncio
async def test_password_reset_admin_not_found():
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AdminNotFoundException):
        await service.password_reset(
            db=db_mock, code=code, email=email, new_password=new_password
        )


@pytest.mark.asyncio
async def test_password_reset_invalid_token():
    db_mock = AsyncMock()

    email = "admin@test.com"
    new_password = "NewValidPassword123!"

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.password = "old_hashed_password"
    mock_admin.reset_token_hash = "invalid_token"
    mock_admin.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(InvalidResetTokenException) as exc_info:
        await service.password_reset(
            db=db_mock, code=None, email=email, new_password=new_password
        )

    assert exc_info.value.detail == "Token inválido ou corrompido"


@pytest.mark.asyncio
async def test_password_reset_expired_token():
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Token expirado
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(
        to_encode, service.settings.secret_key, algorithm=service.settings.algorithm
    )

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(InvalidResetTokenException):
        await service.password_reset(
            db=db_mock, code=code, email=email, new_password=new_password
        )


@pytest.mark.asyncio
async def test_password_reset_weak_password():
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    new_password = "123"  # Senha fraca

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(
        to_encode, service.settings.secret_key, algorithm=service.settings.algorithm
    )

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AdminWeakPasswordException):
        await service.password_reset(
            db=db_mock, code=code, email=email, new_password=new_password
        )


@pytest.mark.asyncio
async def test_password_reset_wrong_code():
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    wrong_code = "654321"
    new_password = "NewValidPassword123!"

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(
        to_encode, service.settings.secret_key, algorithm=service.settings.algorithm
    )

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(InvalidResetTokenException):
        await service.password_reset(
            db=db_mock, code=wrong_code, email=email, new_password=new_password
        )


@pytest.mark.asyncio
async def test_password_reset_expired_code():
    db_mock = AsyncMock()

    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Token expirado
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(
        to_encode, service.settings.secret_key, algorithm=service.settings.algorithm
    )

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_admin
    db_mock.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(InvalidResetTokenException):
        await service.password_reset(
            db=db_mock, code=code, email=email, new_password=new_password
        )
