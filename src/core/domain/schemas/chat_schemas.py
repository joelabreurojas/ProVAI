from pydantic import BaseModel, ConfigDict, Field


class ChatBase(BaseModel):
    """Base schema with shared chat attributes."""

    tutor_id: int
    title: str


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""

    pass


class ChatUpdate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)


class ChatResponse(ChatBase):
    """Schema for returning chat data to the client."""

    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    """Schema for returning chat message data to the client."""

    id: int
    role: str
    content: str
    model_config = ConfigDict(from_attributes=True)


class QueryRequest(BaseModel):
    """Schema for sending a query to the chatbot."""

    query: str


class QueryResponse(BaseModel):
    """Schema for returning a query response from the chatbot."""

    answer: str


class ConversationTurnResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse
