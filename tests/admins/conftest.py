import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture(scope="function")
async def admin_auth_header(client: AsyncClient):
    """Cria um admin e retorna o header de autenticação."""
    user_credentials = {
        "email": "admin.test@example.com",
        "password": "StrongPassword123!"
    }
    # Register admin
    await client.post("/api/admins/register", json=user_credentials)

    # Login to get token
    login_response = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}