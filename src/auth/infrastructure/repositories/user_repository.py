from sqlalchemy.orm import Session

from src.auth.application.protocols import UserRepositoryProtocol
from src.auth.domain.models import User
from src.auth.domain.schemas import UserCreate


class SQLAlchemyUserRepository(UserRepositoryProtocol):
    """Concrete implementation of the user repository using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def add(self, user_create: UserCreate, hashed_password: str) -> User:
        db_user = User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password,
            role="student",  # Default
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user
