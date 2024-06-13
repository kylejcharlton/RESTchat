from datetime import datetime
from fastapi.testclient import TestClient
from backend.main import app


def test_get_all_chats():
    test_client = TestClient(app)
    response = test_client.get("/chats")
    assert response.status_code == 200

    data = response.json()
    assert "meta" in data
    assert "chats" in data
    meta = data["meta"]
    chats = data["chats"]
    assert meta["count"] == len(chats)
    assert "id" in chats[0]
    assert "name" in chats[0]
    assert "user_ids" in chats[0]
    assert "owner_id" in chats[0]
    assert "created_at" in chats[0]
    assert chats == sorted(chats, key=lambda chat: chat["name"])

    # This will error if an invalid iso datetime was received
    datetime.fromisoformat(chats[0]["created_at"])


def test_get_chat():
    # Known chat id in fake_db.json
    chat_id = "e0ec0881a2c645de842ca5dd0fa7985b"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}")
    assert response.status_code == 200

    data = response.json()
    assert "chat" in data
    chat = data["chat"]
    assert "id" in chat
    assert chat["id"] == chat_id
    assert "name" in chat
    assert "user_ids" in chat
    assert "owner_id" in chat
    assert "created_at" in chat

    # This will error if an invalid iso datetime was received
    datetime.fromisoformat(chat["created_at"])


def test_get_invalid_chat():
    chat_id = "invalid_id"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "Chat"
    assert "entity_id" in detail
    assert detail["entity_id"] == chat_id


def test_update_chat():
    # Known chat id in fake_db.json
    chat_id = "e0ec0881a2c645de842ca5dd0fa7985b"
    new_name = "updated chat name"
    update_params = {
        "name": new_name,
    }
    test_client = TestClient(app)
    response = test_client.put(f"/chats/{chat_id}", json=update_params)
    assert response.status_code == 200

    # Verify json keys in response
    data = response.json()
    assert "chat" in data
    chat = data["chat"]
    assert "id" in chat
    assert chat["id"] == chat_id
    assert "name" in chat
    assert chat["name"] == new_name
    assert "user_ids" in chat
    assert "owner_id" in chat
    assert "created_at" in chat

    # Verify post response matches get response for the new user
    response = test_client.get(f"/chats/{chat_id}")
    assert response.status_code == 200
    assert response.json() == data


def test_update_invalid_chat():
    chat_id = "invalid_id"
    update_params = {
        "name": "updated chat name",
    }
    test_client = TestClient(app)
    response = test_client.put(f"/chats/{chat_id}", json=update_params)
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "Chat"
    assert "entity_id" in detail
    assert detail["entity_id"] == chat_id


def test_delete_chat():
    # Known chat id in fake_db.json
    chat_id = "e0ec0881a2c645de842ca5dd0fa7985b"
    test_client = TestClient(app)
    response = test_client.delete(f"/chats/{chat_id}")
    assert response.status_code == 204

    # Verify the chat is actually gone
    response = test_client.get(f"/chats/{chat_id}")
    assert response.status_code == 404


def test_delete_invalid_chat():
    chat_id = "invalid_id"
    test_client = TestClient(app)
    response = test_client.delete(f"/chats/{chat_id}")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "Chat"
    assert "entity_id" in detail
    assert detail["entity_id"] == chat_id


def test_get_chat_messages():
    # Known chat id in fake_db.json
    chat_id = "734eeb9ddaec43b2ab6e289a0d472376"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}/messages")
    assert response.status_code == 200

    # Verify json keys in response
    data = response.json()
    assert "meta" in data
    assert "messages" in data
    meta = data["meta"]
    messages = data["messages"]
    assert meta["count"] == len(messages)
    assert "id" in messages[0]
    assert "user_id" in messages[0]
    assert "text" in messages[0]
    assert "created_at" in messages[0]
    
    # This will error if an invalid iso datetime was received
    datetime.fromisoformat(messages[0]["created_at"])

    assert messages == sorted(messages, key=lambda message: datetime.fromisoformat(message["created_at"]))    


def test_get_invalid_chat_messages():
    chat_id = "invalid_id"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}/messages")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "Chat"
    assert "entity_id" in detail
    assert detail["entity_id"] == chat_id


def test_get_chat_users():
    # Known chat id in fake_db.json
    chat_id = "734eeb9ddaec43b2ab6e289a0d472376"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}/users")
    assert response.status_code == 200

    # Verify json keys in response
    data = response.json()
    assert "meta" in data
    assert "users" in data
    meta = data["meta"]
    users = data["users"]
    assert meta["count"] == len(users)
    assert "id" in users[0]
    assert "created_at" in users[0]
    assert users == sorted(users, key=lambda user: user["id"])

    # This will error if an invalid iso datetime was received
    datetime.fromisoformat(users[0]["created_at"])


def test_get_invalid_chat_users():
    chat_id = "invalid_id"
    test_client = TestClient(app)
    response = test_client.get(f"/chats/{chat_id}/users")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "Chat"
    assert "entity_id" in detail
    assert detail["entity_id"] == chat_id

