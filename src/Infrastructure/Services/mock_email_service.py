import logging
from uuid import UUID

from src.Domain.Ports.Services.i_email_service import IEmailService
from src.Settings.settings import Settings

logger = logging.getLogger(__name__)


class MockEmailService(IEmailService):
    def __init__(self, settings: Settings):
        self._settings = settings

    async def send_email_confirmation(self, to_email: str, token: str) -> None:
        link = f"{self._settings.FRONTEND_URL}/confirm-email?token={token}"
        logger.info(f"========== MOCK EMAIL ==========")
        logger.info(f"TO: {to_email}")
        logger.info(f"SUBJECT: Confirma tu correo")
        print(f"BODY: Por favor entra a este link para confirmar tu correo: {link}")
        logger.info(f"================================")

    async def send_password_reset(self, to_email: str, token: str) -> None:
        link = f"{self._settings.FRONTEND_URL}/reset-password?token={token}"
        logger.info(f"========== MOCK EMAIL ==========")
        logger.info(f"TO: {to_email}")
        logger.info(f"SUBJECT: Restablecer contraseña")
        logger.info(f"BODY: Entra a este link para crear una nueva contraseña: {link}")
        logger.info(f"================================")
