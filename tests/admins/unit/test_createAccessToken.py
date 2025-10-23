import pytest
from acesso_livre_api.src.admins import exceptions, service
from acesso_livre_api.src.admins.schemas import AdminCreate

def test_createAccessToken():
    admin = AdminCreate( 
    email="validadmin@gmail.com",
    password="ValidPass123!")

    token = service.create_access_token(data={"sub": admin.email})

    assert token is not None

def test_createAccessTokenGeneralException(mocker):
    admin = AdminCreate( 
    email="validadmin@gmail.com",
    password="ValidPass123!")

    mocker.patch('acesso_livre_api.src.admins.service.jwt.encode', side_effect=Exception("Token error"))

    with pytest.raises(exceptions.TokenCreationException):
        service.create_access_token(data={"sub": admin.email})