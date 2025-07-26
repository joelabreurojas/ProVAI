from passlib.context import CryptContext

from src.auth.application.protocols import PasswordServiceProtocol


class PasswordService(PasswordServiceProtocol):
    """Concrete implementation for password hashing using passlib."""

    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        password_hash: str = self._pwd_context.hash(password)

        return password_hash

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        verified_password: bool = self._pwd_context.verify(
            plain_password, hashed_password
        )

        return verified_password
