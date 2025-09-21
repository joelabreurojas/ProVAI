from sqlalchemy.orm import Session

from src.core.application.protocols import UserRepositoryProtocol
from src.core.domain.models import User
from src.core.domain.schemas import UserCreate, UserUpdate


class SQLAlchemyUserRepository(UserRepositoryProtocol):
    """Concrete implementation of the user repository using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, user_create: UserCreate, hashed_password: str) -> User:
        db_user = User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self, user: User, user_update: UserUpdate) -> User:
        user.name = user_update.name
        user.email = user_update.email
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, new_hashed_password: str) -> None:
        user.hashed_password = new_hashed_password
        self.db.commit()

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
