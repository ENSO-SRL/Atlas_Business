from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    Clase base con la sesión SQLAlchemy inyectada.
    Todos los repositorios concretos heredan de esta clase.
    No hace commit ni rollback — esa responsabilidad es del controlador.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
