from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send_email_confirmation(self, to_email: str, token: str) -> None:
        """Envía el email con el link de confirmación de cuenta."""
        pass

    @abstractmethod
    async def send_password_reset(self, to_email: str, token: str) -> None:
        """Envía el email con el link para restablecer la contraseña."""
        pass
