from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from .func_log import log_message

SQLALCHEMY_DATABASE_URL = settings.database_url

# Converter URL para async (postgresql:// -> postgresql+asyncpg://)
async_database_url = SQLALCHEMY_DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            log_message("Iniciando nova sessão do banco de dados", level="debug")
            yield session
        finally:
            log_message("Fechando sessão do banco de dados", level="debug")
            await session.close()
