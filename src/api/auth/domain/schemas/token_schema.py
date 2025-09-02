from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Schema for the JWT access token response provided upon successful login.
    """

    access_token: str = Field(
        ...,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        description="The JSON Web Token for authenticating subsequent requests.",
    )
    token_type: str = Field(
        ...,
        examples=["bearer"],
        description="The type of the token, typically 'bearer'.",
    )
