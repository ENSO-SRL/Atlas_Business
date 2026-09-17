from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService


class Argon2PasswordHashingService(IPasswordHashingService):
    def __init__(self):
        # Utiliza los parámetros de seguridad por defecto de pwdlib para Argon2
        # (memory=65536, iterations=3, parallelism=4)
        self._handler = PasswordHash([Argon2Hasher()])

    def hash(self, plain_password: str) -> str:
        return self._handler.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self._handler.verify(plain_password, hashed_password)
