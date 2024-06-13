from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query
from pydantic import Field
from sqlmodel import Session
from backend import database as db
from backend.auth import get_current_user
from backend.entities import *
from backend.schema import UserInDB


chats_router = APIRouter(prefix="/chats", tags=["Chats"])


@chats_router.get("", response_model=ChatCollection)
def get_chats(session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Gets a collection of chats."""

    chats_in_db = db.get_user_chats_by_id(session, user.id)
    chats = [transform_to_chat(c) for c in chats_in_db]
    sort_key = lambda chat: getattr(chat, "name")

    return ChatCollection(
        meta={"count": len(chats)},
        chats=sorted(chats, key=sort_key),
    )


@chats_router.post("", response_model=ChatResponse, response_model_exclude_none=True, status_code=201)
def add_chat(chat_request: ChatPostRequest, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Creates a new chat."""

    chat_in_db = db.create_new_chat(session, user.id, chat_request.name)
    chat = transform_to_chat(chat_in_db)
    
    return ChatResponse(chat=chat)


@chats_router.get("/{chat_id}", response_model=ChatResponse, response_model_exclude_none=True)
def get_chat(
    chat_id: int,
    include: Annotated[list[Literal["messages", "users"]] | None, Query()] = None,
    session: Session = Depends(db.get_session),
    user: UserInDB = Depends(get_current_user)):
    """Gets a chat for a given id."""

    chat_in_db = db.get_chat_by_id(session, chat_id)
    
    if user not in chat_in_db.users:
        raise NoPermissionException(error_description="requires permission to view chat")

    chat = transform_to_chat(chat_in_db)
    messages = None
    users = None

    if include:
        if "messages" in include:
            messages = [transform_to_message(m) for m in chat_in_db.messages]
        if "users" in include:
            users = [transform_to_user(u) for u in chat_in_db.users]

    return ChatResponse(
        meta={
            "message_count": len(chat_in_db.messages),
            "user_count": len(chat_in_db.users),
        },
        chat=chat,
        messages=messages,
        users=users,
    )


@chats_router.put("/{chat_id}", response_model=ChatResponse, response_model_exclude_none=True)
def update_chat(chat_id: str, request: ChatRequest, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Updates the name of a chat for a given id."""

    chat_in_db = db.get_chat_by_id(session, chat_id)

    if chat_in_db.owner != user:
        raise NoPermissionException(error_description="requires permission to edit chat")

    chat_in_db = db.update_chat_by_id(session, chat_id, request.name)

    return ChatResponse(
        chat=transform_to_chat(chat_in_db),
    )


@chats_router.get("/{chat_id}/messages", response_model=MessageCollection)
def get_chat_messages(chat_id: int,  session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Gets a collection of messages for a given chat id."""

    chat_in_db = db.get_chat_by_id(session, chat_id)
    
    if user not in chat_in_db.users:
        raise NoPermissionException(error_description="requires permission to view chat")

    messages_in_db = db.get_chat_messages_by_id(session, chat_id)
    messages = [transform_to_message(m) for m in messages_in_db]
    sort_key = lambda message: getattr(message, "created_at")

    return MessageCollection(
        meta={"count": len(messages)},
        messages=sorted(messages, key=sort_key),
    )


@chats_router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=201)
def add_message_to_chat(chat_id: int, new_message: MessagePostRequest,  session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Adds a message to a chat."""

    chat_in_db = db.get_chat_by_id(session, chat_id)
    
    if user not in chat_in_db.users:
        raise NoPermissionException(error_description="requires permission to view chat")

    message = db.add_message_to_chat_by_id(session, chat_id, user.id, new_message.text)
    return MessageResponse(message=transform_to_message(message))


@chats_router.put("/{chat_id}/messages/{message_id}", response_model=MessageResponse)
def edit_message_in_chat(chat_id: int, message_id: int, updated_message: MessagePostRequest,  session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Edits a message in a chat."""

    chat = db.get_chat_by_id(session, chat_id)
    message = db.get_message_by_id(session, message_id)
    if message.user != user:
        raise NoPermissionException(error_description="requires permission to edit message")

    message = db.update_message_by_id(session, message_id, updated_message.text)

    return MessageResponse(message=transform_to_message(message))


@chats_router.delete("/{chat_id}/messages/{message_id}", status_code=204)
def delete_message_in_chat(chat_id: int, message_id: int,  session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Deletes a message in a chat."""

    chat = db.get_chat_by_id(session, chat_id)
    message = db.get_message_by_id(session, message_id)
    if message.user != user:
        raise NoPermissionException(error_description="requires permission to edit message")

    message = db.delete_message_by_id(session, message_id)


@chats_router.get("/{chat_id}/users", response_model=UserCollection)
def get_chat_users(chat_id: int, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Gets a collection of users for a given chat id."""

    chat_in_db = db.get_chat_by_id(session, chat_id)

    if user not in chat_in_db.users:
        raise NoPermissionException(error_description="requires permission to view chat")

    users_in_db = db.get_chat_users_by_id(session, chat_id)
    users = [transform_to_user(u) for u in users_in_db]
    sort_key = lambda message: getattr(message, "id")

    return UserCollection(
        meta={"count": len(users)},
        users=sorted(users, key=sort_key),
    )


@chats_router.put("/{chat_id}/users/{user_id}", response_model=UserCollection, response_model_exclude_none=True, status_code=201)
def add_new_chat_user(chat_id: int, user_id: int, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Adds a user to a chat."""

    chat_in_db = db.get_chat_by_id(session, chat_id)

    if chat_in_db.owner != user:
        raise NoPermissionException(error_description="requires permission to edit chat members")

    users_in_db = db.add_user_to_chat_by_id(session, chat_id, user_id)
    users = [transform_to_user(u) for u in users_in_db]
    sort_key = lambda message: getattr(message, "id")

    return UserCollection(
        meta={"count": len(users)},
        users=sorted(users, key=sort_key),
    )


@chats_router.delete("/{chat_id}/users/{user_id}", response_model=UserCollection, response_model_exclude_none=True)
def remove_chat_user(chat_id: int, user_id: int, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Removes a user from a chat."""

    chat_in_db = db.get_chat_by_id(session, chat_id)

    if chat_in_db.owner != user:
        raise NoPermissionException(error_description="requires permission to edit chat members")
    
    if chat_in_db.owner_id == user_id:
        raise InvalidStateException(error_description="owner of a chat cannot be removed")

    
    users_in_db = db.remove_user_from_chat_by_id(session, chat_id, user_id)
    users = [transform_to_user(u) for u in users_in_db]
    sort_key = lambda message: getattr(message, "id")

    return UserCollection(
        meta={"count": len(users)},
        users=sorted(users, key=sort_key),
    )

