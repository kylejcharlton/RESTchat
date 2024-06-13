import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
import sqlalchemy
from sqlmodel import Session, SQLModel, select
from typing import Annotated

from backend import database as db
from backend.entities import UserResponse, transform_to_user
from backend.schema import UserInDB


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
access_token_duration = 3600 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
jwt_key = os.environ.get("JWT_KEY", default="a423707127f7d1e2f7f03c255f514a62abaceb3110369430f60dc1a0c094c5e9")
jwt_alg = "HS256"

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegistration(SQLModel):
    """Request model to register new user."""

    username: str
    email: str
    password: str


class AccessToken(BaseModel):
    """Response model for access token."""

    access_token: str
    token_type: str
    expires_in: int


class Claims(BaseModel):
    """Access token claims (aka payload)."""

    sub: str
    exp: int


class DuplicateEntityException(HTTPException):
    def __init__(self, name: str, field: str, value: str):
        super().__init__(
            status_code=422,
            detail={
                "type": "duplicate_value",
                "entity_name": name,
                "entity_field": field,
                "entity_value": value,
            },
        )


class DuplicateUsernameException(DuplicateEntityException):
    def __init__(self, value: str):
        super().__init__(
            name="User",
            field="username",
            value=value,
        )


class DuplicateEmailException(DuplicateEntityException):
    def __init__(self, value: str):
        super().__init__(
            name="User",
            field="email",
            value=value,
        )


class AuthException(HTTPException):
    def __init__(self, error: str, description: str):
        super().__init__(
            status_code=401,
            detail={
                "error": error,
                "error_description": description,
            },
        )


class InvalidCredentials(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="invalid username or password",
        )


class InvalidToken(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="invalid access token",
        )


class ExpiredToken(AuthException):
    def __init__(self):
        super().__init__(
            error="invalid_client",
            description="expired bearer token",
        )


def get_current_user(
    session: Session = Depends(db.get_session),
    token: str = Depends(oauth2_scheme),
) -> UserInDB:
    """FastAPI dependency to get current user from bearer token."""
    user = _decode_access_token(session, token)
    return user


def update_user_by_id(session: Session, user_id: str, new_username: str | None, new_email: str | None) -> UserInDB:
    """Updates a user's email and/or username"""

    user = db.get_user_by_id(session, user_id)

    if new_username:
        setattr(user, "username", new_username)
    if new_email:
        setattr(user, "email", new_email)
    session.add(user)

    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()

        m = str(e.orig)
        if m.startswith("UNIQUE constraint failed:"):
            if (m.find("users.email") >= 0):
                raise DuplicateEmailException(new_email)
            if (m.find("users.username") >= 0):
                raise DuplicateUsernameException(new_username)
            raise e
    
    session.refresh(user)
    return user


@auth_router.post("/registration", response_model=UserResponse, status_code=201)
def register_user(
    registration: UserRegistration,
    session: Annotated[Session, Depends(db.get_session)],
):
    """Register new user."""

    hashed_password = pwd_context.hash(registration.password)
    user = UserInDB(
        **registration.model_dump(),
        hashed_password=hashed_password,
    )
    session.add(user)

    try:
        session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()

        m = str(e.orig)
        if m.startswith("UNIQUE constraint failed:"):
            if (m.find("users.email") >= 0):
                raise DuplicateEmailException(registration.email)
            if (m.find("users.username") >= 0):
                raise DuplicateUsernameException(registration.username)
            raise e
        
    session.refresh(user)
    return UserResponse(user=transform_to_user(user))


@auth_router.post("/token", response_model=AccessToken)
def get_access_token(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(db.get_session),
):
    """Get access token for user."""

    user = _get_authenticated_user(session, form)
    return _build_access_token(user)


def _get_authenticated_user(
    session: Session,
    form: OAuth2PasswordRequestForm,
) -> UserInDB:
    user = session.exec(
        select(UserInDB).where(UserInDB.username == form.username)
    ).first()

    if user is None or not pwd_context.verify(form.password, user.hashed_password):
        raise InvalidCredentials()

    return user


def _build_access_token(user: UserInDB) -> AccessToken:
    expiration = int(datetime.now(timezone.utc).timestamp()) + access_token_duration
    claims = Claims(sub=str(user.id), exp=expiration)
    access_token = jwt.encode(claims.model_dump(), key=jwt_key, algorithm=jwt_alg)

    return AccessToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=access_token_duration,
    )


def _decode_access_token(session: Session, token: str) -> UserInDB:
    try:
        claims_dict = jwt.decode(token, key=jwt_key, algorithms=[jwt_alg])
        claims = Claims(**claims_dict)
        user_id = claims.sub
        user = session.get(UserInDB, user_id)

        if user is None:
            raise InvalidToken()

        return user
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()
    except ValidationError:
        raise InvalidToken()
