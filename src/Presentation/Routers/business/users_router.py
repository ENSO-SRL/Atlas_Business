from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Business.create_business_user import CreateBusinessUserCommand, CreateBusinessUserUseCase
from src.Application.UseCases.Business.list_business_users import ListBusinessUsersCommand, ListBusinessUsersUseCase
from src.Application.UseCases.Business.update_business_user import UpdateBusinessUserCommand, UpdateBusinessUserUseCase
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Infrastructure.Security.argon2_password_hashing_service import Argon2PasswordHashingService
from src.Presentation.Dependencies.auth import UserContext, require_admin
from src.Presentation.Dependencies.repositories import get_business_user_repo, get_user_repo
from src.Presentation.Schemas.business_schemas import CreateUserRequest, UpdateUserRequest

router = APIRouter()


@router.get("/")
async def list_business_users(
    user: UserContext = Depends(require_admin),
    user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    use_case = ListBusinessUsersUseCase(user_repo)
    command = ListBusinessUsersCommand(business_id=user.business_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.post("/", status_code=201)
async def create_business_user(
    body: CreateUserRequest,
    user: UserContext = Depends(require_admin),
    user_repo: IUserRepository = Depends(get_user_repo),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    hashing_service = Argon2PasswordHashingService()
    use_case = CreateBusinessUserUseCase(user_repo, business_user_repo, hashing_service)
    
    command = CreateBusinessUserCommand(
        business_id=user.business_id,
        actor_id=user.user_id,
        roles=body.roles,
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        plain_password=body.password,
    )
    result = await use_case.execute(command)
    return result


@router.patch("/{user_id}")
async def update_business_user(
    user_id: UUID,
    body: UpdateUserRequest,
    user: UserContext = Depends(require_admin),
    user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    use_case = UpdateBusinessUserUseCase(user_repo)
    
    command = UpdateBusinessUserCommand(
        user_id=user_id,
        business_id=user.business_id,
        actor_id=user.user_id,
        roles=body.roles,
        is_active=body.is_active,
    )
    result = await use_case.execute(command)
    return result
