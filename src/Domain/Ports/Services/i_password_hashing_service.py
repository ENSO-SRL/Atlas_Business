from abc import ABC, abstractmethod


class IPasswordHashingService(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Genera el hash seguro de una contraseña en texto plano."""
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica que un texto plano coincide con su hash almacenado."""
        ...
