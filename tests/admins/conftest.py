import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture(scope="function")
async def admin_auth_header(client: AsyncClient, db_session):
    """Cria um admin e retorna o header de autenticação."""
    from acesso_livre_api.src.admins.models import Admins
    from acesso_livre_api.src.admins.service import get_password_hash
    from datetime import datetime, timezone

    user_credentials = {
        "email": "admin.test@example.com",
        "password": "StrongPassword123!"
    }

    # Create admin directly in DB using the test session
    hashed_password = get_password_hash(user_credentials["password"])
    new_admin = Admins(
        email=user_credentials["email"],
        password=hashed_password,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(new_admin)
    await db_session.commit()

    # Login to get token
    login_response = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}

    # Login to get token
    login_response = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}