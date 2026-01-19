from os import environ
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

load_dotenv()

def getenv(config: str) -> str:
    value = environ.get(config)
    if not value:
        raise ValueError(f"{config} is missing from .env.")
    return value

DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_LOCATION = getenv("DB_LOCATION")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

# Use asyncpg driver for async Postgres
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_LOCATION}:{DB_PORT}/{DB_NAME}"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Async dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

