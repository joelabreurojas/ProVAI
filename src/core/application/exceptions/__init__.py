from .ai_exceptions import ModelConfigurationError, ModelLoadError, ModelNotFoundError
from .auth_exceptions import (
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidPasswordError,
    TokenExpiredError,
    TokenInvalidScopeError,
    TokenMissingDataError,
    TokenValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from .chat_exceptions import ChatNotFoundError, MessageCreationError
from .common_exceptions import AppException, DatabaseError
from .rag_exceptions import (
    DocumentNotFoundError,
    IngestionError,
    PDFParsingError,
    UnsupportedFileTypeError,
)
from .tutor_exceptions import (
    InvitationEmailMismatchError,
    InvitationNotFoundError,
    SelfEnrollmentError,
    TutorNotFoundError,
    TutorOwnershipError,
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)

__all__ = [
    "ModelConfigurationError",
    "ModelLoadError",
    "ModelNotFoundError",
    "InsufficientPermissionsError",
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "TokenExpiredError",
    "TokenInvalidScopeError",
    "TokenMissingDataError",
    "TokenValidationError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "ChatNotFoundError",
    "MessageCreationError",
    "AppException",
    "DatabaseError",
    "DocumentNotFoundError",
    "IngestionError",
    "PDFParsingError",
    "UnsupportedFileTypeError",
    "InvitationEmailMismatchError",
    "InvitationNotFoundError",
    "SelfEnrollmentError",
    "TutorNotFoundError",
    "TutorOwnershipError",
    "UserAlreadyEnrolledError",
    "UserNotEnrolledError",
]
