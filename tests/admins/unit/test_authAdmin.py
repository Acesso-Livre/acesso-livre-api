from unittest.mock import MagicMock

from acesso_livre_api.src.admins import service
from acesso_livre_api.src.admins.schemas import AdminCreate


def test_auth_admin_success():
    # Mock da sessão do banco de dados
    db_mock = MagicMock()

    # Hash da senha correta
    hashedpassword = service.get_password_hash("ValidPass123!")

    # Mockar a query para simular que o email existe e a senha está correta
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(email="validadmin@gmail.com", password=hashedpassword)
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    # Criar um admin
    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    # Verificar se a autenticação é bem-sucedida
    result = service.authenticate_admin(db_mock, admin.email, admin.password)
    assert result is not None
    assert result.email == admin.email
    assert result.password == hashedpassword


def test_auth_admin_invalid_email():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    result = service.authenticate_admin(db_mock, admin.email, admin.password)
    assert result is None

def test_auth_admin_invalid_password():
    db_mock = MagicMock()

    hashedpassword = service.get_password_hash("ValidPass123!")

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(email="validadmin@gmail.com", password=hashedpassword)
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    

    result = service.authenticate_admin(db_mock, admin.email, "WrongPass123!")
    assert result is None