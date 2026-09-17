from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base declarativa compartida por todos los modelos ORM del proyecto.
    Todos los modelos en Infrastructure/Persistence/Models deben heredar de esta clase.
    """
    pass


def build_engine(database_url: str):
    """
    Construye el engine async de SQLAlchemy.
    La URL debe usar el esquema postgresql+asyncpg://
    Ej: postgresql+asyncpg://user:password@localhost:5432/atlas_b2b
    """
    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )


def build_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """
    Construye la fábrica de sesiones async.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
