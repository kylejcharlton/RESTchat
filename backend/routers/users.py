from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend import database as db
from backend.auth import get_current_user, update_user_by_id
from backend.entities import (
    UserPutRequest,
    UserResponse,
    UserCollection,
    ChatCollection,
    transform_to_chat,
    transform_to_user,
)
from backend.schema import UserInDB


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("", response_model=UserCollection)
def get_users(session: Session = Depends(db.get_session)):
    """Get a collection of users."""

    users_in_db = db.get_all_users(session)
    users = [transform_to_user(u) for u in users_in_db]
    sort_key = lambda user: getattr(user, "id")

    return UserCollection(
        meta={"count": len(users)},
        users=sorted(users, key=sort_key),
    )


@users_router.get("/me", response_model=None)
def get_self(user: UserInDB = Depends(get_current_user)):
    """Gets the currently logged in user."""

    return UserResponse(user=transform_to_user(user))


@users_router.put("/me", response_model=UserResponse)
def update_current_user(request: UserPutRequest, session: Session = Depends(db.get_session), user: UserInDB = Depends(get_current_user)):
    """Updates the currently logged in user."""

    user = update_user_by_id(session, user.id, request.username, request.email)
    return UserResponse(user=transform_to_user(user))


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(db.get_session)):
    """Get an user for a given id."""

    return UserResponse(user=transform_to_user(db.get_user_by_id(session, user_id)))


@users_router.get("/{user_id}/chats", response_model=ChatCollection)
def get_user_chats(user_id: int, session: Session = Depends(db.get_session)):
    """Get a collection of a user's chats for a given user id."""

    chats_in_db = db.get_user_chats_by_id(session, user_id)
    chats = [transform_to_chat(c) for c in chats_in_db]
    sort_key = lambda chat: getattr(chat, "name")

    return ChatCollection(
        meta={"count": len(chats)},
        chats=sorted(chats, key=sort_key),
    )

