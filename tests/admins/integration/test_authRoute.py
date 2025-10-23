import pytest
from httpx import AsyncClient

from acesso_livre_api.src.admins import exceptions

user_credentials = {
    "email": "auth.user@empresa.com",
    "password": "Senha1234!"
}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Testa o login com sucesso e a obtenção de um token de acesso."""

    user_to_register = {
        "email": "auth.user@empresa.com",
        "password": "Senha1234!"
    }
    await client.post("/api/admins/register", json=user_to_register)

    res = await client.post("/api/admins/login", json=user_credentials)
    
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Testa o login com uma senha incorreta."""
    wrong_credentials = user_credentials.copy()
    wrong_credentials["password"] = "wrongpassword"
    
    res = await client.post("/api/admins/login", json=wrong_credentials)
    
    assert res.status_code == 401
    assert res.json()["detail"] == "Email ou senha incorretos"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    """Testa o login com um email que não está registrado."""
    nonexistent_credentials = {
        "email": "nao.existe@empresa.com",
        "password": "anypassword"
    }
    
    res = await client.post("/api/admins/login", json=nonexistent_credentials)
    
    assert res.status_code == 401
    assert res.json()["detail"] == "Email ou senha incorretos"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_check_token_success(client: AsyncClient):
    """Testa a validação de um token de acesso válido."""
    user_to_register = {
        "email": "auth.user@empresa.com",
        "password": "Senha1234!"
    }
    await client.post("/api/admins/register", json=user_to_register)

    login_res = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    res = await client.get("/api/admins/check-token", headers=headers)
    
    assert res.status_code == 200
    assert res.json() == {"valid": True}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_check_token_no_token(client: AsyncClient):
    """Testa a rota de verificação de token sem fornecer um token."""
    res = await client.get("/api/admins/check-token")
    
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"

@pytest.mark.integration
@pytest.mark.asyncio
# testar a excecao que 'e retoranada quando nao consegue criar o token
async def test_check_token_error_creating_token(client: AsyncClient, monkeypatch):
    """Testa a validação de token quando ocorre um erro na criação do token."""
    user_to_register = {
        "email": "auth.user@empresa.com",
        "password": "Senha1234!"
    }

    await client.post("/api/admins/register", json=user_to_register)
    login_res = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    monkeypatch.setattr("acesso_livre_api.src.admins.service.verify_token", lambda token: (_ for _ in ()).throw(exceptions.TokenCreationException()))

    res = await client.get("/api/admins/check-token", headers=headers)
    assert res.status_code == 500
    assert res.json()["detail"] == "Erro ao criar token de acesso"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check_token_expired_token(client: AsyncClient, monkeypatch):
    """Testa a validação de um token expirado."""
    user_to_register = {
        "email": "auth.user@empresa.com",
        "password": "Senha1234!"
    }

    await client.post("/api/admins/register", json=user_to_register)

    login_res = await client.post("/api/admins/login", json=user_credentials)

    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    monkeypatch.setattr("acesso_livre_api.src.admins.service.verify_token", lambda token: False)

    res = await client.get("/api/admins/check-token", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"valid": False}