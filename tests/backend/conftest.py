import datetime
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from backend.main import app
from backend import auth, database as db
from backend.schema import ChatInDB, UserInDB


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session):
    def _get_session_override():
        return session

    app.dependency_overrides[db.get_session] = _get_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def user_fixture(session):
    def _build_user(
            username: str = "john",
            email: str = "john@test.email",
            password: str = "strong_password",
    ) -> UserInDB:
        return auth.register_user(
            auth.UserRegistration(
                username=username,
                email=email,
                password=password,
            ),
            session,
        )

    return _build_user

