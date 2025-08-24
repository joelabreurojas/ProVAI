from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TutorBase(BaseModel):
    """Base schema with shared tutor attributes."""

    course_name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    roadmap: dict[str, Any] | None = Field(None)


class TutorCreate(TutorBase):
    """Schema for creating a new tutor."""

    pass


class TutorResponse(TutorBase):
    """Schema for returning tutor data to the client."""

    id: int
    teacher_id: int
    model_config = ConfigDict(from_attributes=True)


class TutorInvitationCreate(BaseModel):
    """Schema for inviting a batch of students to a tutor."""

    student_emails: list[EmailStr] = Field(
        ..., description="A list of unique student email addresses to invite."
    )


class TutorInvitationResponse(BaseModel):
    """Schema for returning the status of a created invitation."""

    email: EmailStr
    status: str
    token: str | None = None
    model_config = ConfigDict(from_attributes=True)


class StudentEnrollmentCreate(BaseModel):
    """Schema for a student to enroll using an invitation token."""

    invitation_token: str = Field(..., description="The JWT invitation token.")


class StudentEnrollmentResponse(BaseModel):
    """Schema confirming a successful enrollment."""

    tutor_id: int
    user_id: int
    role: str
    model_config = ConfigDict(from_attributes=True)
