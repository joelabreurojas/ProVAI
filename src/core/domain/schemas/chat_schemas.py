from pydantic import BaseModel, ConfigDict


class ChatBase(BaseModel):
    """Base schema with shared chat attributes."""

    tutor_id: int
    title: str


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""

    pass


class ChatResponse(ChatBase):
    """Schema for returning chat data to the client."""

    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Schema for returning chat message data to the client."""

    role: str
    content: str
    model_config = ConfigDict(from_attributes=True)


class QueryRequest(BaseModel):
    """Schema for sending a query to the chatbot."""

    query: str


class QueryResponse(BaseModel):
    """Schema for returning a query response from the chatbot."""

    answer: str
