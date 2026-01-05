from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from core.config import get_settings
import os

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL
#DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session









# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# from sqlalchemy.orm import declarative_base
# from core.config import get_settings
# from typing import AsyncGenerator
#
# settings = get_settings()
#
# DATABASE_URL = settings.DATABASE_URL
#
# engine = create_async_engine(DATABASE_URL, echo=True)
#
# SessionLocal = async_sessionmaker(
#     bind=engine,
#     expire_on_commit=False,
# )
#
# Base = declarative_base()
#
#
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         yield session
#



