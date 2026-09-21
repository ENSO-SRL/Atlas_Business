from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.user import User
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Infrastructure.Persistence.Models.user_model import UserModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class UserRepository(BaseRepository, IUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: User) -> User:
        model = UserModel(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_email_verified=entity.is_email_verified,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.first() is not None
