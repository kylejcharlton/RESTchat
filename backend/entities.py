from datetime import datetime
from pydantic import BaseModel
from backend.schema import ChatInDB, MessageInDB, UserInDB


class NoPermissionException(Exception):
    def __init__(self, *, error_description: str):
        self.error_description = error_description


class InvalidStateException(Exception):
    def __init__(self, *, error_description: str):
        self.error_description = error_description


class Metadata(BaseModel):
    count: int


class ChatMetadata(BaseModel):
    message_count: int
    user_count: int


class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class UserResponse(BaseModel):
    user: User


class UserRequest(BaseModel):
    id: int


class Message(BaseModel):
    id: int
    text: str
    chat_id: int
    user: User
    created_at: datetime


class MessageResponse(BaseModel):
    message: Message


class MessagePostRequest(BaseModel):
    text: str


class MessagePutRequest(BaseModel):
    text: str


class Chat(BaseModel):
    id: int
    name: str
    owner: User
    created_at: datetime


class ChatResponse(BaseModel):
    meta: ChatMetadata | None = None
    chat: Chat
    messages: list[Message] | None = None
    users: list[User] | None = None


class ChatRequest(BaseModel):
    name: str


class ChatPostRequest(BaseModel):
    name: str


class UserPutRequest(BaseModel):
    username: str | None = None
    email: str | None = None


class UserCollection(BaseModel):
    meta: Metadata | None = None
    users: list[User]


class ChatCollection(BaseModel):
    meta: Metadata
    chats: list[Chat]


class MessageCollection(BaseModel):
    meta: Metadata
    messages: list[Message]


def transform_to_chat(c: ChatInDB):
    return Chat(
        id=c.id,
        name=c.name,
        owner=User(**c.owner.model_dump()),
        created_at=c.created_at,
    )


def transform_to_message(m: MessageInDB):
    return Message(
        id=m.id,
        text=m.text,
        chat_id=m.chat_id,
        user=User(**m.user.model_dump()),
        created_at=m.created_at,
    )


def transform_to_user(u: UserInDB):
    return User(**u.model_dump())