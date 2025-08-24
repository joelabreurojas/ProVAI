from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema with shared user attributes."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["John Doe"],
        description="The user's full name.",
    )
    email: EmailStr = Field(
        ...,
        examples=["jhondoe@me.com"],
        description="The user's unique email address.",
    )


class UserCreate(UserBase):
    """Schema for creating a new user. This is the data sent from the client."""

    password: str = Field(
        ...,
        min_length=8,
        examples=["My_SecurePassword123"],
        description="The user's password (will be hashed before storage).",
    )


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
