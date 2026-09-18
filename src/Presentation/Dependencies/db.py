from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Provee la sesión de base de datos asíncrona.
    El session_factory se encuentra en request.app.state.session_factory.
    """
    session_factory = request.app.state.session_factory
    
    async with session_factory() as session:
        async with session.begin():
            yield session
