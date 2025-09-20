import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base schema with shared user attributes."""

    name: str = Field(
        ...,
        examples=["John Doe"],
        description="The user's full name.",
    )
    email: EmailStr = Field(
        ...,
        examples=["jhondoe@me.com"],
        description="The user's unique email address.",
    )

    @field_validator("name")
    @classmethod
    def validate_name_length(cls, value: str) -> str:
        """
        Validates that the name meets requirements:
        - At least 2 characters
        - At most 100 characters
        """
        if len(value) < 2:
            raise ValueError("Name must be at least 2 characters long.")
        if len(value) > 100:
            raise ValueError("Name must be at most 100 characters long.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        """
        Validates that the email address is in a valid format.
        """
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
            raise ValueError("Invalid email address format.")
        return value


class UserCreate(UserBase):
    """Schema for creating a new user. This is the data sent from the client."""

    password: str = Field(
        ...,
        examples=["My_SecurePassword123"],
        description="The user's password (will be hashed before storage).",
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        """
        Validates that the password meets complexity requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%_^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")
        return value


class UserUpdate(UserBase):
    """Schema for updating a user's profile information."""

    pass


class PasswordUpdate(BaseModel):
    """Schema for updating a user's password."""

    current_password: str
    new_password: str = Field(..., alias="new_password")  # Use alias to match form name
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        """
        Validates that the password meets complexity requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%_^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")
        return value


class UserResponse(UserBase):
    """
    Schema for returning user data to the client.
    Crucially, this schema does NOT include the password.
    """

    id: int = Field(..., examples=[1], description="The user's unique identifier.")
    role: str = Field(
        ...,
        examples=["teacher"],
        description="The user's global role in the system.",
    )

    model_config = ConfigDict(from_attributes=True)
