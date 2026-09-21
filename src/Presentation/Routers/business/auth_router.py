from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from src.Application.UseCases.Auth.register_user import RegisterUserCommand, RegisterUserUseCase
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Infrastructure.Security.argon2_password_hashing_service import Argon2PasswordHashingService
from src.Presentation.Dependencies.repositories import get_user_repo

router = APIRouter()

class RegisterUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str | None = None

@router.post("/register", status_code=201)
async def register_user(
    body: RegisterUserRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
):
    password_service = Argon2PasswordHashingService()
    use_case = RegisterUserUseCase(user_repo, password_service)
    command = RegisterUserCommand(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        plain_password=body.password,
        phone=body.phone,
    )
    result = await use_case.execute(command)
    return result

# Nota: endpoints de login, refresh, logout y select-business se implementarán 
# cuando se reanude el plan completo de autenticación JWT.
