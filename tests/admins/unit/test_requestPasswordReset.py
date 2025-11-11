import pytest
from unittest.mock import MagicMock
from acesso_livre_api.src.admins import exceptions, service

def test_request_password_reset_success():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = MagicMock(email="validadmin@gmail.com")
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    result = service.request_password_reset(db_mock, "validadmin@gmail.com")

    assert result is not None
    assert result == {"message": "Enviamos um link de recuperação ao email."}
    db_mock.commit.assert_called_once()

def test_request_password_reset_admin_not_found():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    with pytest.raises(exceptions.AdminNotFoundException):
        service.request_password_reset(db_mock, "validadmin@gmail.com")

def test_request_password_reset_general_exception():
    db_mock = MagicMock()

    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.side_effect = Exception("DB error")
    mock_query.filter.return_value = mock_filter
    db_mock.query.return_value = mock_query

    with pytest.raises(Exception):
        service.request_password_reset(db_mock, "validadmin@gmail.com")