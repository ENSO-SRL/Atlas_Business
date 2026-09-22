from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import UserNotFoundError
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository


@dataclass
class GetUserProfileQuery:
    user_id: UUID
    business_id: UUID | None = None


@dataclass
class BusinessContextResult:
    business_id: UUID
    business_name: str
    roles: list[str]
    is_active: bool


@dataclass
class UserProfileResult:
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    is_email_verified: bool
    business_context: BusinessContextResult | None
    is_superadmin: bool


class GetUserProfileUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        business_user_repo: IBusinessUserRepository,
    ):
        self._user_repo = user_repo
        self._business_user_repo = business_user_repo

    async def execute(self, query: GetUserProfileQuery) -> UserProfileResult:
        user = await self._user_repo.get_by_id(query.user_id)
        if not user:
            raise UserNotFoundError("Usuario no encontrado.")

        business_context = None

        if query.business_id:
            business_user = await self._business_user_repo.get_by_user_and_business(
                user_id=query.user_id, business_id=query.business_id
            )
            if business_user:
                business_context = BusinessContextResult(
                    business_id=business_user.business_id,
                    business_name=business_user.business_name,
                    roles=[role.value for role in business_user.roles],
                    is_active=business_user.is_active
                )

        return UserProfileResult(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            is_email_verified=user.is_email_verified,
            business_context=business_context,
            is_superadmin=user.is_superadmin,
        )
