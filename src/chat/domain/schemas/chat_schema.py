from pydantic import BaseModel, ConfigDict


class ChatBase(BaseModel):
    tutor_id: int
    title: str


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    role: str
    content: str
    model_config = ConfigDict(from_attributes=True)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
