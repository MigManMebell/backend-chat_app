from pydantic import BaseModel
from datetime import datetime
from typing import List

# Forward declaration for circular dependencies
class Message(BaseModel):
    pass

class UserBase(BaseModel):
    email: str
    nickname: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    avatar_url: str | None = None
    # messages: List[Message] = [] # This creates circular dependency issues, handle it differently if needed

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    sender_id: int
    sender: User

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
