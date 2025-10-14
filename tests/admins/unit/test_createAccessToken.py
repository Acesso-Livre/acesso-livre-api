from acesso_livre_api.src.admins import service
from acesso_livre_api.src.admins.schemas import AdminCreate


def test_createAccessToken():
    admin = AdminCreate( 
    email="validadmin@gmail.com",
    password="ValidPass123!")

    token = service.create_access_token(data={"sub": admin.email})

    assert token is not None