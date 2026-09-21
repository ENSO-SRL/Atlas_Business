from fastapi import Depends

from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService
from src.Domain.Ports.Services.i_token_service import ITokenService
from src.Infrastructure.Security.argon2_password_hashing_service import Argon2PasswordHashingService
from src.Infrastructure.Security.jwt_token_service import JwtTokenService
from src.Presentation.Dependencies.auth import get_settings
from src.Settings.settings import Settings


def get_password_hashing_service() -> IPasswordHashingService:
    return Argon2PasswordHashingService()


def get_token_service(settings: Settings = Depends(get_settings)) -> ITokenService:
    return JwtTokenService(settings)
