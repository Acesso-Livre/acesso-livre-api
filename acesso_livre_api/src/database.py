from .func_log import log_message
from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

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
    pool_size=10,        # Conexões permanentes (Supabase Free: ~60 max)
    max_overflow=15,     # Conexões extras sob demanda
    pool_timeout=30,     # Timeout para obter conexão
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            log_message("Database session closed.", level="debug", logger_name="acesso_livre_api")
            await session.close()
            
