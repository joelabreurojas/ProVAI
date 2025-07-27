from pydantic import BaseModel, Field


class Token(BaseModel):
    """Schema for the JWT access token response."""

    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(..., examples=["bearer"])
