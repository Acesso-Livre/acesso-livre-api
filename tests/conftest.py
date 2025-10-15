# Only for integration tests
# it's used to create a test database and override the get_db dependency
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from acesso_livre_api.src.main import app
from acesso_livre_api.src.database import get_db, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
connection = test_engine.connect()
Base.metadata.create_all(bind=connection)
TestingSessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client