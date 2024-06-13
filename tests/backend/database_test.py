from backend.entities import *


def test_relationship(session):
    user = UserInDB(
        username="joe",
        email="try@me.com",
        hashed_password="hashed_password",
    )

    chat = ChatInDB(
        name="test_chat",
        owner=user,
        users=[user],
    )

    message = MessageInDB(
        text="This is a test message",
        user=user,
        chat=chat,
    )
    
    session.add(user)
    session.add(chat)
    session.add(message)
    session.commit()
    session.refresh(message)
    session.refresh(chat)
    session.refresh(user)

    assert chat in user.chats
    assert user == chat.owner
    assert user in chat.users
    assert message in chat.messages
    assert user == message.user
    assert chat == message.chat
