from sqlalchemy import select
from sqlmodel import Session, SQLModel, create_engine, select
from backend.entities import ( 
    Chat,
)
from backend.schema import (
    UserInDB, MessageInDB, ChatInDB
)


engine = create_engine(
    "sqlite:///backend/RESTchat.db",
    echo=True,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class EntityNotFoundException(Exception):
    def __init__(self, *, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id


def get_all_users(session: Session) -> list[UserInDB]:
    return session.exec(select(UserInDB)).all()


def get_user_by_id(session: Session, user_id: int) -> UserInDB:
    user = session.get(UserInDB, user_id)
    if user:
        return user
    raise EntityNotFoundException(entity_name="User", entity_id=user_id)


def get_user_chats_by_id(session: Session, user_id: int) -> list[ChatInDB]:
    user = get_user_by_id(session, user_id)
    return user.chats


def get_all_chats(session: Session) -> list[ChatInDB]:
    return session.exec(select(ChatInDB)).all()


def create_new_chat(session: Session, user_id: int, chat_name: str) -> ChatInDB:
    chat = ChatInDB(owner_id=user_id, name=chat_name)
    
    session.add(chat)
    session.commit()
    session.refresh(chat)

    add_user_to_chat_by_id(session, chat.id, user_id)
    
    return chat


def get_chat_by_id(session: Session, chat_id: int) -> ChatInDB:
    chat = session.get(ChatInDB, chat_id)
    if chat:
        return chat
    raise EntityNotFoundException(entity_name="Chat", entity_id=chat_id)


def get_message_by_id(session: Session, message_id: int) -> MessageInDB:
    message = session.get(MessageInDB, message_id)
    if message:
        return message
    raise EntityNotFoundException(entity_name="Message", entity_id=message_id)


def update_message_by_id(session: Session, message_id: int, updated_text: str) -> MessageInDB:
    message_in_db = get_message_by_id(session, message_id)

    setattr(message_in_db, "text", updated_text)
    session.add(message_in_db)
    session.commit()
    session.refresh(message_in_db)

    return message_in_db


def delete_message_by_id(session: Session, message_id: int) -> None:
    message_in_db = get_message_by_id(session, message_id)
    session.delete(message_in_db)
    session.commit()


def update_chat_by_id(session: Session, chat_id: int, new_name: str) -> ChatInDB:

    chat_in_db = get_chat_by_id(session, chat_id)

    setattr(chat_in_db, "name", new_name)
    session.add(chat_in_db)
    session.commit()
    session.refresh(chat_in_db)

    return chat_in_db


def add_user_to_chat_by_id(session: Session, chat_id: int, user_id: int) -> list[UserInDB]:

    user_in_db = get_user_by_id(session, user_id)
    chat_in_db = get_chat_by_id(session, chat_id)

    if user_in_db not in chat_in_db.users:
        chat_in_db.users.append(user_in_db)
        session.add(chat_in_db)
        session.commit()
        session.refresh(chat_in_db)

    return chat_in_db.users


def remove_user_from_chat_by_id(session: Session, chat_id: int, user_id: int) -> list[UserInDB]:
    user_in_db = get_user_by_id(session, user_id)
    chat_in_db = get_chat_by_id(session, chat_id)

    if user_in_db in chat_in_db.users:
        chat_in_db.users.remove(user_in_db)
        session.add(chat_in_db)
        session.commit()
        session.refresh(chat_in_db)
    
    return chat_in_db.users


def add_message_to_chat_by_id(session: Session, chat_id: int, user_id: int, text: str):

    get_chat_by_id(session, chat_id)
    message = MessageInDB(
        text=text,
        user_id=user_id,
        chat_id=chat_id,
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def get_chat_messages_by_id(session: Session, chat_id: int) -> list[MessageInDB]:
    chat = get_chat_by_id(session, chat_id)
    return chat.messages


def get_chat_users_by_id(session: Session, chat_id: int) -> list[UserInDB]:
    chat = get_chat_by_id(session, chat_id)
    return chat.users

