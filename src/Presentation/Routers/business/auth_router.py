import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Response, Request
from pydantic import BaseModel, EmailStr

from src.Application.UseCases.Auth.register_user import RegisterUserCommand, RegisterUserUseCase
from src.Application.UseCases.Auth.login_user import LoginUserCommand, LoginUserUseCase
from src.Application.UseCases.Auth.select_business import SelectBusinessCommand, SelectBusinessUseCase
from src.Application.UseCases.Auth.refresh_access_token import RefreshAccessTokenCommand, RefreshAccessTokenUseCase
from src.Application.UseCases.Auth.logout_user import LogoutUserCommand, LogoutUserUseCase
from src.Application.UseCases.Auth.get_user_profile import GetUserProfileQuery, GetUserProfileUseCase
from src.Application.UseCases.Auth.list_user_businesses import ListUserBusinessesCommand, ListUserBusinessesUseCase
from src.Application.UseCases.Auth.request_email_confirmation import RequestEmailConfirmationCommand, RequestEmailConfirmationUseCase
from src.Application.UseCases.Auth.confirm_email import ConfirmEmailCommand, ConfirmEmailUseCase
from src.Application.UseCases.Auth.request_password_reset import RequestPasswordResetCommand, RequestPasswordResetUseCase
from src.Application.UseCases.Auth.reset_password import ResetPasswordCommand, ResetPasswordUseCase

from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Repositories.i_token_blacklist_repository import ITokenBlacklistRepository
from src.Domain.Ports.Repositories.i_email_token_repository import IEmailTokenRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService
from src.Domain.Ports.Services.i_token_service import ITokenService
from src.Domain.Ports.Services.i_email_service import IEmailService

from src.Presentation.Dependencies.repositories import get_user_repo, get_business_user_repo, get_token_blacklist_repo, get_email_token_repo
from src.Presentation.Dependencies.services import get_password_hashing_service, get_token_service, get_email_service
from src.Presentation.Dependencies.auth import get_current_user, UserContext, get_refresh_token_from_cookie
from src.Presentation.Schemas.business_schemas import PaginatedUserBusinessesResponse

router = APIRouter()

_logger = logging.getLogger(__name__)

class RegisterUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SelectBusinessRequest(BaseModel):
    business_id: UUID


class ConfirmEmailRequest(BaseModel):
    token: UUID


class RequestEmailConfirmationRequest(BaseModel):
    email: EmailStr


class RequestPasswordResetRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: UUID
    new_password: str


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str | None = None):
    # SameSite=Lax (o None si hay frontend separado). Usamos HttpOnly siempre.
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )


def _clear_auth_cookies(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")


@router.post("/register", status_code=201)
async def register_user(
    body: RegisterUserRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
    password_service: IPasswordHashingService = Depends(get_password_hashing_service),
    email_token_repo: IEmailTokenRepository = Depends(get_email_token_repo),
    email_service: IEmailService = Depends(get_email_service),
):
    use_case = RegisterUserUseCase(user_repo, password_service)
    command = RegisterUserCommand(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        plain_password=body.password,
        phone=body.phone,
    )
    result = await use_case.execute(command)
    _logger.info(f"Usuario registrado: {result.email}")

    # Enviar correo de confirmación automáticamente
    email_use_case = RequestEmailConfirmationUseCase(user_repo, email_token_repo, email_service)
    email_command = RequestEmailConfirmationCommand(email=result.email)
    await email_use_case.execute(email_command)
    _logger.info(f"Correo de confirmación enviado para usuario: {result.email}")

    return result


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    user_repo: IUserRepository = Depends(get_user_repo),
    password_service: IPasswordHashingService = Depends(get_password_hashing_service),
    token_service: ITokenService = Depends(get_token_service),
):
    use_case = LoginUserUseCase(user_repo, password_service, token_service)
    command = LoginUserCommand(email=body.email, plain_password=body.password)
    result = await use_case.execute(command)

    _set_auth_cookies(response, access_token=result.access_token, refresh_token=result.refresh_token)
    return {"message": "Login exitoso."}


@router.get("/user")
async def get_user(
    user_context: UserContext = Depends(get_current_user),
    user_repo: IUserRepository = Depends(get_user_repo),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    use_case = GetUserProfileUseCase(user_repo, business_user_repo)
    query = GetUserProfileQuery(
        user_id=user_context.user_id,
        business_id=user_context.business_id,
    )
    return await use_case.execute(query)


@router.get("/me/businesses", response_model=PaginatedUserBusinessesResponse)
async def list_user_businesses(
    page: int = 1,
    page_size: int = 20,
    user_context: UserContext = Depends(get_current_user),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    use_case = ListUserBusinessesUseCase(business_user_repo)
    command = ListUserBusinessesCommand(
        user_id=user_context.user_id,
        page=page,
        page_size=page_size
    )
    items, total = await use_case.execute(command)
    return {"items": items, "total": total}


@router.post("/select-business")
async def select_business(
    body: SelectBusinessRequest,
    response: Response,
    user_context: UserContext = Depends(get_current_user),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
    token_service: ITokenService = Depends(get_token_service),
):
    use_case = SelectBusinessUseCase(business_user_repo, token_service)
    command = SelectBusinessCommand(
        user_id=user_context.user_id,
        business_id=body.business_id
    )
    result = await use_case.execute(command)

    # Solo sobreescribe el access_token; el refresh_token se mantiene igual
    _set_auth_cookies(response, access_token=result.access_token)
    return {"message": "Negocio seleccionado exitosamente."}


@router.post("/refresh")
async def refresh_access_token(
    response: Response,
    # Si intentamos leer el user_context aquí, fallará si el access_token expiró.
    # Necesitamos poder refrescar incluso si access_token no existe, leyendo solo el refresh_token
    # pero queremos mantener el business context. Para eso leemos del payload viejo si podemos
    # o mejor aún, no pasamos dependencias restrictivas.
    # Un momento, RefreshAccessTokenUseCase decodificará el refresh. No podemos
    # saber el context_business anterior desde el refresh_token (no lo guardamos ahí para no invalidarlo si cambia rol).
    # Opcional: el cliente puede volver a llamar select_business. O podríamos extraer payload ignorando exp.
    refresh_token: str = Depends(get_refresh_token_from_cookie),
    token_blacklist_repo: ITokenBlacklistRepository = Depends(get_token_blacklist_repo),
    token_service: ITokenService = Depends(get_token_service),
    request: Request = None,
):
    # Intentamos obtener current_business_id del access_token viejo (ignorando expiración)
    current_business_id = None
    current_roles = None
    is_superadmin = False
    old_access_token = request.cookies.get("access_token") if request else None
    if old_access_token:
        try:
            # decodificamos ignorando firma/expiración solo para rescatar el contexto
            from jose import jwt
            unverified_payload = jwt.get_unverified_claims(old_access_token)
            print(unverified_payload)
            b_id_str = unverified_payload.get("business_id")
            is_superadmin = unverified_payload.get("is_superadmin")
            if b_id_str:
                current_business_id = UUID(b_id_str) 
                current_roles = unverified_payload.get("roles")
        except Exception as e:
            print(f"Error al decodificar access_token: {e}") 
            pass

    use_case = RefreshAccessTokenUseCase(token_blacklist_repo, token_service)
    command = RefreshAccessTokenCommand(
        refresh_token=refresh_token,
        current_business_id=current_business_id,
        current_roles=current_roles,
        is_superadmin=is_superadmin,
    )
    result = await use_case.execute(command)

    _set_auth_cookies(response, access_token=result.access_token)
    return {"message": "Token renovado."}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str = Depends(get_refresh_token_from_cookie),
    token_blacklist_repo: ITokenBlacklistRepository = Depends(get_token_blacklist_repo),
    token_service: ITokenService = Depends(get_token_service),
):
    use_case = LogoutUserUseCase(token_blacklist_repo, token_service)
    command = LogoutUserCommand(refresh_token=refresh_token)
    await use_case.execute(command)

    _clear_auth_cookies(response)
    return {"message": "Cierre de sesión exitoso."}


@router.post("/request-email-confirmation")
async def request_email_confirmation(
    body: RequestEmailConfirmationRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
    email_token_repo: IEmailTokenRepository = Depends(get_email_token_repo),
    email_service: IEmailService = Depends(get_email_service),
):
    _logger.info(f"Solicitud de confirmación de correo para usuario: {body.email}")
    use_case = RequestEmailConfirmationUseCase(user_repo, email_token_repo, email_service)
    command = RequestEmailConfirmationCommand(email=body.email)
    await use_case.execute(command)
    _logger.info(f"Correo de confirmación enviado para usuario: {body.email}")
    return {"message": "Si el correo está registrado, se enviará un enlace de confirmación."}


@router.post("/confirm-email")
async def confirm_email(
    body: ConfirmEmailRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
    email_token_repo: IEmailTokenRepository = Depends(get_email_token_repo),
):
    use_case = ConfirmEmailUseCase(user_repo, email_token_repo)
    command = ConfirmEmailCommand(token=body.token)
    await use_case.execute(command)
    return {"message": "Correo confirmado exitosamente."}


@router.post("/request-password-reset")
async def request_password_reset(
    body: RequestPasswordResetRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
    email_token_repo: IEmailTokenRepository = Depends(get_email_token_repo),
    email_service: IEmailService = Depends(get_email_service),
):
    use_case = RequestPasswordResetUseCase(user_repo, email_token_repo, email_service)
    command = RequestPasswordResetCommand(email=body.email)
    await use_case.execute(command)
    return {"message": "Si el correo está registrado, se ha enviado un enlace para restablecer la contraseña."}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    user_repo: IUserRepository = Depends(get_user_repo),
    email_token_repo: IEmailTokenRepository = Depends(get_email_token_repo),
    password_service: IPasswordHashingService = Depends(get_password_hashing_service),
):
    use_case = ResetPasswordUseCase(user_repo, email_token_repo, password_service)
    command = ResetPasswordCommand(token=body.token, new_password=body.new_password)
    await use_case.execute(command)
    return {"message": "Contraseña restablecida exitosamente."}
