import datetime
from typing import Any, Callable

from jose import jwt
from sqlalchemy.orm import Session

from src.applicaiton.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.application.protocols import AuthServiceProtocol
from src.domain.models import User
from src.domain.schemas import UserCreate
from src.infrastructure.settings import settings


class AuthService(AuthServiceProtocol):
    def __init__(
        self,
        db: Session,
        password_hasher: Callable[[str], str],
        password_verifier: Callable[[str, str], bool],
    ) -> None:
        self.db = db
        self.get_password_hash = password_hasher
        self.verify_password_hash = password_verifier

    def register_user(self, user_create: UserCreate) -> User:
        db_user = self.db.query(User).filter(User.email == user_create.email).first()

        if db_user:
            raise UserAlreadyExistsError()

        hashed_password = self.get_password_hash(user_create.password)
        new_user = User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password,
            role="student",  # Default for now
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        valid_password = self.verify_password_hash(password, user.hashed_password)

        if not user or not valid_password:
            raise InvalidCredentialsError()

        return user

    def create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()

        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return encoded_jwt
