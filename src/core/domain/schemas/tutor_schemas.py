from typing import Annotated, Any

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TutorBase(BaseModel):
    """Base schema with shared tutor attributes."""

    course_name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    roadmap: dict[str, Any] | None = Field(None)


class TutorCreate(TutorBase):
    """Schema for creating a new tutor."""

    @classmethod
    def as_form(
        cls,
        course_name: Annotated[str, Form(min_length=3, max_length=100)],
        description: Annotated[str | None, Form(max_length=500)] = None,
        # Roadmap cannot be sent via a simple form, so it's omitted
    ) -> "TutorCreate":
        return cls(course_name=course_name, description=description)


class TutorUpdate(BaseModel):
    """
    Schema for updating a tutor's details. All fields are optional.
    """

    course_name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)


class TutorResponse(TutorBase):
    """Schema for returning tutor data to the client."""

    id: int
    teacher_id: int
    model_config = ConfigDict(from_attributes=True)


class TutorResponseWithToken(TutorResponse):
    """
    Extends TutorResponse to include the invitation token.
    This should only be returned to the tutor's owner.
    """

    token: str


class TutorInvitationCreate(BaseModel):
    """Schema for inviting a batch of students to a tutor."""

    tutor_id: int
    student_emails: list[EmailStr]


class TutorInvitationResponse(BaseModel):
    """Schema for returning the single, shareable invitation token."""

    tutor_id: int
    invitation_token: str
    status: str


class StudentEnrollmentCreate(BaseModel):
    """Schema for a student to enroll using an invitation token."""

    invitation_token: str = Field(..., description="The JWT invitation token.")


class StudentEnrollmentResponse(BaseModel):
    """Schema confirming a successful enrollment."""

    tutor_id: int
    user_id: int
    role: str
    model_config = ConfigDict(from_attributes=True)
