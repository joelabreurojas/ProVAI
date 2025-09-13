import bcrypt

from src.core.application.protocols import PasswordServiceProtocol


class PasswordService(PasswordServiceProtocol):
    """Concrete implementation for password hashing using bcrypt directly."""

    def get_password_hash(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        return hashed_password.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        plain_password_bytes = plain_password.encode("utf-8")
        hashed_password_bytes = hashed_password.encode("utf-8")

        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
