from fastapi import Depends

from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService
from src.Domain.Ports.Services.i_token_service import ITokenService
from src.Domain.Ports.Services.i_email_service import IEmailService
from src.Domain.Ports.Services.i_rnc_validation_service import IRncValidationService
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService
from src.Domain.Ports.Services.i_external_agent_identity_service import IExternalAgentIdentityService
from src.Infrastructure.Security.argon2_password_hashing_service import Argon2PasswordHashingService
from src.Infrastructure.Security.jwt_token_service import JwtTokenService
from src.Infrastructure.Services.mock_email_service import MockEmailService
from src.Infrastructure.Services.mock_rnc_validation_service import MockRncValidationService
from src.Infrastructure.Services.dummy_content_filter_service import DummyContentFilterService
from src.Infrastructure.Services.dummy_external_agent_identity_service import DummyExternalAgentIdentityService
from src.Presentation.Dependencies.auth import get_settings
from src.Settings.settings import Settings


def get_password_hashing_service() -> IPasswordHashingService:
    return Argon2PasswordHashingService()


def get_token_service(settings: Settings = Depends(get_settings)) -> ITokenService:
    return JwtTokenService(settings)


def get_email_service(settings: Settings = Depends(get_settings)) -> IEmailService:
    return MockEmailService(settings)


def get_rnc_validation_service() -> IRncValidationService:
    return MockRncValidationService()


def get_content_filter_service() -> IContentFilterService:
    return DummyContentFilterService()


def get_identity_service() -> IExternalAgentIdentityService:
    return DummyExternalAgentIdentityService()
