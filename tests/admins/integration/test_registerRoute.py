import pytest

user = {
        "email": "admin@empresa.com",
        "password": "Senha1234!"
    }

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_success(client, admin_auth_header):
    """Testa o registro de um novo administrador com sucesso."""
    res = await client.post("/api/admins/register", json=user, headers=admin_auth_header)

    assert res.status_code == 201
    assert res.json() == {"status": "success"}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_existing_email(client, admin_auth_header):
    """Testa o registro de um administrador com um email já existente."""
    await client.post("/api/admins/register", json=user, headers=admin_auth_header)
    
    res = await client.post("/api/admins/register", json=user, headers=admin_auth_header)

    assert res.status_code == 409
    assert res.json()["detail"] == "Administrador com este email já existe"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_invalid_email(client, admin_auth_header):
    """Testa o registro de um administrador com um email inválido."""
    userInvalidEmail = {
        "email": "invalid.#email@de.com",
        "password": "Senha1234!"
    }
    res = await client.post("/api/admins/register", json=userInvalidEmail, headers=admin_auth_header)

    assert res.status_code == 422
    assert res.json()["detail"] == "O email fornecido não é válido"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_weak_password(client, admin_auth_header):
    """Testa o registro de um administrador com uma senha fraca."""
    userWeakPass = {
        "email": "admin.weakpass@empresa.com",
        "password": "senha12345"
    }

    res = await client.post("/api/admins/register", json=userWeakPass, headers=admin_auth_header)

    assert res.status_code == 422
    assert res.json()["detail"] == "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_general_error(client, admin_auth_header):
    """Testa o registro de um administrador com payload vazio, esperando um erro de validação."""
    res = await client.post("/api/admins/register", json={}, headers=admin_auth_header)

    assert res.status_code == 422
    response_json = res.json()
    assert response_json["detail"] == "Ocorreram erros de validação."

    error_fields = [error['field'] for error in response_json['errors']]
    assert 'email' in error_fields
    assert 'password' in error_fields