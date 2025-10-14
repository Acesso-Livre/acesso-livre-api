from acesso_livre_api.src.admins import service

def test_get_password_hash():
    password = "StrongPassword123!"
    hashed = service.get_password_hash(password)
    assert service.verify_password(password, hashed)

    wrong_password = "WrongPassword!"
    assert not service.verify_password(wrong_password, hashed)