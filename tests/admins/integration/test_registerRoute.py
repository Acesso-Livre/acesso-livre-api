import pytest

user = {
        "email": "admin@empresa.com",
        "password": "Senha1234!"
    }

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_success(client):
    """Testa o registro de um novo administrador com sucesso."""
    res = await client.post("/api/admins/register", json=user)

    assert res.status_code == 201
    assert res.json() == {"status": "success"}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_existing_email(client):
    """Testa o registro de um administrador com um email já existente."""
    await client.post("/api/admins/register", json=user)
    
    res = await client.post("/api/admins/register", json=user)

    assert res.status_code == 409
    assert res.json()["detail"] == "Administrador com este email já existe"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Testa o registro de um administrador com um email inválido."""
    userInvalidEmail = {
        "email": "invalid.#email@de.com",
        "password": "Senha1234!"
    }
    res = await client.post("/api/admins/register", json=userInvalidEmail)

    assert res.status_code == 400
    assert res.json()["detail"] == "O email fornecido não é válido"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_weak_password(client):
    """Testa o registro de um administrador com uma senha fraca."""
    userWeakPass = {
        "email": "admin.weakpass@empresa.com",
        "password": "senha12345"
    }

    res = await client.post("/api/admins/register", json=userWeakPass)

    assert res.status_code == 400
    assert res.json()["detail"] == "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_general_error(client):
    """Testa o registro de um administrador que causa um erro geral (simulado)."""
    res = await client.post("/api/admins/register", json={})

    assert res.status_code == 500
    assert res.json()["detail"] == "Erro interno ao processar solicitação"