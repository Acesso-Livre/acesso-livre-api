import pytest 
from unittest.mock import MagicMock
from acesso_livre_api.src.admins import service, exceptions
from acesso_livre_api.src.admins.schemas import AdminCreate
from pydantic import ValidationError

def test_create_admin_email_exists():
    # Mock da sessão do banco de dados
    db_mock = MagicMock()

    # Mockar a query para simular que o email já existe
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(email="validadmin@gmail.com")
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query
    
    # Criar um admin com email que já existe
    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    # Verificar se a exceção correta é levantada
    with pytest.raises(exceptions.AdminAlreadyExistsException):
        service.create_admin(db_mock, admin)

def test_create_admin_success():
    db_mock = MagicMock();

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    result = service.create_admin(db_mock, admin)
    assert result is True
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()


def test_create_admin_weak_password():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="invalidpass!")
    
    with pytest.raises(exceptions.AdminWeakPasswordException):
        service.create_admin(db_mock, admin)


def test_create_admin_invalid_email():
    with pytest.raises(exceptions.AdminInvalidEmailException):
         AdminCreate( 
        email="usuario!invalido@dominio.com",
        password="ValidPass123!")

def test_create_admin_empty_email():
    with pytest.raises(ValidationError):
         AdminCreate( 
        email="",
        password="ValidPass123!")
         
def teste_create_admin_empty_password():
    with pytest.raises(ValidationError):
         AdminCreate( 
        email="validadmin@gmail.com",
        password="")

def test_create_admin_general_exception():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    # Simular uma exceção genérica ao adicionar o admin
    db_mock.add.side_effect = Exception("Database error")

    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    with pytest.raises(exceptions.AdminCreationException):
        service.create_admin(db_mock, admin)
    db_mock.add.assert_called_once()
    db_mock.commit.assert_not_called()
    db_mock.refresh.assert_not_called()