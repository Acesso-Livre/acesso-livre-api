from unittest.mock import MagicMock
import pytest
from datetime import datetime, timezone, timedelta

from acesso_livre_api.src import exceptions
from acesso_livre_api.src.admins import service
from acesso_livre_api.src.admins.exceptions import AdminNotFoundException, InvalidResetTokenException, AdminWeakPasswordException

def test_password_reset_success():
    # Mocks e Configuração Inicial
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Simular um token de reset valido, como se tivesse sido gerado antes
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(to_encode, service.settings.secret_key, algorithm=service.settings.algorithm)

    # Criar o mock do admin que sera "encontrado" no banco
    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.password = "old_hashed_password"
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    # Configurar o mock do DB para retornar o mock do admin
    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin

    # Chamar a funcao a ser testada
    result = service.password_reset(
        db=db_mock,
        code=code,
        email=email,
        new_password=new_password
    )

    # A senha do admin foi atualizada para o hash da nova senha?
    assert service.verify_password(new_password, mock_admin.password)
    
    # O token de reset foi invalidado?
    assert mock_admin.reset_token_hash is None
    assert mock_admin.reset_token_expires is None

    # As alteracoes foram salvas no banco?
    db_mock.commit.assert_called_once()
    
    # A funcao retornou a mensagem de sucesso?
    assert result == {"message": "Senha atualizada com sucesso!"}


def test_password_reset_admin_not_found():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    db_mock.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(AdminNotFoundException):
        service.password_reset(
            db=db_mock,
            code=code,
            email=email,
            new_password=new_password
        )

def test_password_reset_invalid_token():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    new_password = "NewValidPassword123!"

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.password = "old_hashed_password"
    mock_admin.reset_token_hash = "invalid_token"
    mock_admin.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin

    with pytest.raises(InvalidResetTokenException) as exc_info:
        service.password_reset(
            db=db_mock,
            code=None,
            email=email,
            new_password=new_password
        )
    
    assert exc_info.value.detail == "Token inválido ou corrompido"

def test_password_reset_expired_token():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Token expirado
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(to_encode, service.settings.secret_key, algorithm=service.settings.algorithm)

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin

    with pytest.raises(InvalidResetTokenException) as exc_info:
        service.password_reset(
            db=db_mock,
            code=code,
            email=email,
            new_password=new_password
        )

def test_password_reset_weak_password():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    new_password = "123"  # Senha fraca

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(to_encode, service.settings.secret_key, algorithm=service.settings.algorithm)

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin

    with pytest.raises(AdminWeakPasswordException):
        service.password_reset(
            db=db_mock,
            code=code,
            email=email,
            new_password=new_password
        )

def test_password_reset_wrong_code():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    wrong_code = "654321"
    new_password = "NewValidPassword123!"

    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(to_encode, service.settings.secret_key, algorithm=service.settings.algorithm)

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token
    mock_admin.reset_token_expires = expire

    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin

    with pytest.raises(InvalidResetTokenException):
        service.password_reset(
            db=db_mock,
            code=wrong_code,
            email=email,
            new_password=new_password
        )

def test_password_reset_expired_code():
    db_mock = MagicMock()
    
    email = "admin@test.com"
    code = "123456"
    new_password = "NewValidPassword123!"

    # Token expirado
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode = {"sub": email, "exp": expire, "code": code}
    reset_token = service.jwt.encode(to_encode, service.settings.secret_key, algorithm=service.settings.algorithm)

    mock_admin = MagicMock()
    mock_admin.email = email
    mock_admin.reset_token_hash = reset_token   
    mock_admin.reset_token_expires = expire
    db_mock.query.return_value.filter.return_value.first.return_value = mock_admin
    
    with pytest.raises(InvalidResetTokenException) as exc_info:
        service.password_reset(
            db=db_mock,
            code=code,
            email=email,
            new_password=new_password
        )