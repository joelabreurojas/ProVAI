from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema with shared user attributes."""

    name: str = Field(..., examples=["John Doe"])
    email: EmailStr = Field(..., examples=["jhondoe@me.com"])


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, examples=["MySecurePassword123"])


class UserResponse(UserBase):
    """Schema for returning user data to the client."""

    id: int = Field(..., examples=[1])
    role: str = Field(..., examples=["teacher"])

    model_config = ConfigDict(from_attributes=True)
