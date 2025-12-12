import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from acesso_livre_api.src.database import Base, get_db
from acesso_livre_api.src.locations.models import AccessibilityItem
from acesso_livre_api.src.comments import models as comments_models
from acesso_livre_api.src.admins import models as admins_models
from acesso_livre_api.src.main import app

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# Enable foreign key support for SQLite
@event.listens_for(test_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
Base.metadata.bind = test_engine


async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    # Initialize database
    await init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    # Clear table data (do not drop tables)
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.run_sync(lambda c: c.execute(table.delete()))


@pytest_asyncio.fixture(scope="function")
async def created_accessibility_item(db_session):
    """Cria um item de acessibilidade para testes."""
    item = AccessibilityItem(name="Item Teste", icon_url="icon.svg")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item


@pytest_asyncio.fixture(scope="function")
async def created_location(
    client: AsyncClient, created_accessibility_item, admin_auth_header
):
    """Cria um local com itens de acessibilidade para testes."""
    location_data = {
        "name": "Local de Teste",
        "description": "Descrição do local",
        "top": 10.0,
        "left": 20.0,
    }
    response = await client.post(
        "/api/locations/", json=location_data, headers=admin_auth_header
    )
    assert response.status_code == 201, f"Failed to create location: {response.text}"
    return response.json()


@pytest_asyncio.fixture(scope="function")
async def admin_auth_header(client: AsyncClient):
    """Cria um admin e retorna o header de autenticação."""
    user_credentials = {
        "email": "admin.test@example.com",
        "password": "StrongPassword123!",
    }
    # Register admin
    await client.post("/api/admins/register", json=user_credentials)

    # Login to get token
    login_response = await client.post("/api/admins/login", json=user_credentials)
    access_token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
