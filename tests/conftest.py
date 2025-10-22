import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Import Base and models to ensure they are registered
from acesso_livre_api.src.database import Base, get_db


# Test database configuration in shared memory
# Uses file::memory: with cache=shared to allow multiple connections to the same database
SQLALCHEMY_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables in test database BEFORE importing the app
Base.metadata.create_all(bind=test_engine)

# Now import the app after tables are created
from acesso_livre_api.src.main import app

# Override get_db dependency to use test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

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