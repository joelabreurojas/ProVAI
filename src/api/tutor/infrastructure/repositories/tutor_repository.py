from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import joinedload

from src.core.application.protocols import TutorRepositoryProtocol
from src.core.domain.models import Document, Invitation, Tutor, User
from src.core.domain.schemas import TutorCreate, TutorUpdate


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

    def get_tutor_by_token(self, token: str) -> Tutor | None:
        """Retrieves a single tutor by its unique invitation token."""
        return self.db.query(Tutor).filter(Tutor.token == token).first()

    def get_tutors_for_user(self, user: User) -> list[Tutor]:
        """
        Retrieves all tutors a user is associated with, either as a
        teacher or an enrolled student.
        """
        if user.role == "teacher":
            # Teachers see all tutors they've created
            return self.db.query(Tutor).filter(Tutor.teacher_id == user.id).all()

        # Students see tutors they are enrolled in
        user_with_tutors = (
            self.db.query(User)
            .filter(User.id == user.id)
            .options(joinedload(User.enrolled_tutors))
            .one()
        )
        return sorted(user_with_tutors.enrolled_tutors, key=lambda t: t.course_name)

    def update_tutor(self, tutor: Tutor, tutor_update: TutorUpdate) -> Tutor:
        """Updates a tutor's attributes in the database."""
        update_data = tutor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tutor, key, value)

        self.db.add(tutor)
        self.db.commit()
        self.db.refresh(tutor)
        return tutor

    def add_authorized_emails(self, tutor: Tutor, emails: list[str]) -> None:
        """Adds new, unique emails to the tutor's invitation whitelist."""
        existing_emails = {auth.student_email for auth in tutor.authorized_students}
        for email in set(emails):  # De-duplicate input list
            if email not in existing_emails:
                new_auth = Invitation(tutor_id=tutor.id, student_email=email)
                self.db.add(new_auth)
        self.db.commit()

    def get_authorized_emails(self, tutor: Tutor) -> list[str]:
        """Retrieves the list of emails authorized to enroll in the tutor."""
        return [auth.student_email for auth in tutor.authorized_students]

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

    def remove_authorized_email(self, tutor: Tutor, email: str) -> None:
        """Removes a single email from the tutor's invitation whitelist."""
        auth_entry = (
            self.db.query(Invitation)
            .filter_by(tutor_id=tutor.id, student_email=email)
            .first()
        )
        if auth_entry:
            self.db.delete(auth_entry)
            self.db.commit()

    def remove_student_by_email(self, tutor: Tutor, email: str) -> None:
        """
        Atomically removes a student's access by email. It deletes the entry
        from the invitation whitelist and, if a corresponding user is enrolled,
        removes them from the tutor's student roster.
        """
        # Remove from the whitelist
        auth_entry = (
            self.db.query(Invitation)
            .filter_by(tutor_id=tutor.id, student_email=email)
            .first()
        )
        if auth_entry:
            self.db.delete(auth_entry)

        # Find the user and remove from the roster
        user_to_remove = self.db.query(User).filter_by(email=email).first()
        if user_to_remove and user_to_remove in tutor.students:
            tutor.students.remove(user_to_remove)

        self.db.commit()

    def remove_student_from_tutor(self, tutor: Tutor, student: User) -> None:
        """Removes the many-to-many link to unenroll a student from a tutor."""
        if student in tutor.students:
            tutor.students.remove(student)
            self.db.commit()

    def remove_document_from_tutor(self, tutor: Tutor, document: Document) -> None:
        """Removes the many-to-many link between a tutor and a document."""
        if document in tutor.documents:
            tutor.documents.remove(document)
            self.db.commit()

    def delete_tutor(self, tutor_id: int) -> None:
        """Finds a tutor by ID and deletes it from the database."""
        tutor = self.db.get(Tutor, tutor_id)  # efficient way to fetch by PK
        if tutor:
            self.db.delete(tutor)
            self.db.commit()
