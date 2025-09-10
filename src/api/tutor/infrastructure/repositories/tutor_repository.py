from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import joinedload

from src.api.auth.domain.models import User
from src.api.rag.domain.models import Document
from src.api.tutor.application.protocols import TutorRepositoryProtocol
from src.api.tutor.domain.models import Tutor
from src.api.tutor.domain.schemas import TutorCreate


class SQLAlchemyTutorRepository(TutorRepositoryProtocol):
    """
    Concrete implementation of the Tutor repository using SQLAlchemy.
    """

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_tutor(self, tutor_create: TutorCreate, teacher_id: int) -> Tutor:
        """Creates a new Tutor record in the database."""
        db_tutor = Tutor(**tutor_create.model_dump(), teacher_id=teacher_id)
        self.db.add(db_tutor)
        self.db.commit()
        self.db.refresh(db_tutor)
        return db_tutor

    def get_tutor_by_id(self, tutor_id: int) -> Tutor | None:
        """Retrieves a single tutor by its primary key, eagerly loading students."""
        return (
            self.db.query(Tutor)
            .options(joinedload(Tutor.students))
            .filter(Tutor.id == tutor_id)
            .first()
        )

    def get_tutors_for_user(self, user: User) -> list[Tutor]:
        """
        Retrieves all tutors a user is associated with, either as a
        teacher or an enrolled student.
        """
        if user.role == "teacher":
            # Teachers see all tutors they've created
            return self.db.query(Tutor).filter(Tutor.teacher_id == user.id).all()

        # Students see tutors they are enrolled in (requires loading the relationship)
        user_with_tutors = (
            self.db.query(User)
            .filter(User.id == user.id)
            .options(joinedload(User.enrolled_tutors))
            .one()
        )
        return sorted(user_with_tutors.enrolled_tutors, key=lambda t: t.course_name)

    def add_student_to_tutor(self, tutor: Tutor, student: User) -> None:
        """
        Creates the many-to-many link to enroll a student in a tutor.
        This method is idempotent; it will not create a duplicate enrollment.
        """
        if student not in tutor.students:
            tutor.students.append(student)
            self.db.commit()

    def link_document_to_tutor(self, tutor: Tutor, document: Document) -> None:
        """Creates the many-to-many link between a tutor and a document."""
        if document not in tutor.documents:
            tutor.documents.append(document)
            self.db.commit()

    def remove_document_from_tutor(self, tutor: Tutor, document: Document) -> None:
        """Removes the many-to-many link between a tutor and a document."""
        if document in tutor.documents:
            tutor.documents.remove(document)
            self.db.commit()

    def get_chunk_hashes_for_tutor(self, tutor_id: int) -> list[str]:
        """
        Performs an efficient query to get all unique chunk hashes for all
        documents related to a specific tutor.
        """
        tutor = (
            self.db.query(Tutor)
            .options(joinedload(Tutor.documents).joinedload(Document.chunks))
            .filter(Tutor.id == tutor_id)
            .first()
        )
        if not tutor:
            return []

        unique_chunk_hashes = {
            chunk.content_hash
            for document in tutor.documents
            for chunk in document.chunks
        }
        return list(unique_chunk_hashes)
