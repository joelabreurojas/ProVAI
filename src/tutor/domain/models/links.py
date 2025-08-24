from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.infrastructure.database import Base

tutor_students = Table(
    "tutor_students",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)
