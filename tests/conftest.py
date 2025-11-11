import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from acesso_livre_api.src.database import Base, get_db
from acesso_livre_api.src.locations.models import AccessibilityItem
from acesso_livre_api.src.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# Enable foreign key support for SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    # Recreate tables before each test to ensure they exist
    Base.metadata.create_all(bind=test_engine)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    # Clear only table data (do not drop tables)
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest_asyncio.fixture(scope="function")
def created_accessibility_item(db_session):
    """Cria um item de acessibilidade para testes."""
    item = AccessibilityItem(name="Item Teste", icon_url="icon.svg", top=10, left=10)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest_asyncio.fixture(scope="function")
async def created_location(
    client: AsyncClient, created_accessibility_item, admin_auth_header
):
    """Cria um local com itens de acessibilidade para testes."""
    location_data = {
        "name": "Local de Teste",
        "description": "Descrição do local",
        "accessibility_item_ids": [created_accessibility_item.id],
    }
    response = await client.post(
        "/api/locations/", json=location_data, headers=admin_auth_header
    )
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
