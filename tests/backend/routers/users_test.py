from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.main import app
import json


def test_get_all_users(client, user_fixture):
    db_users = [user_fixture(username=u[0], email=u[1]) for u in [["jimmy", "jimmy@test.com"], ["sally", "sally@generic.email"]]]
    response = client.get("/users")
    assert response.status_code == 200

    data = response.json()

    meta = data["meta"]
    users = data["users"]

    assert meta["count"] == len(db_users)
    assert {user["username"] for user in users} == {
        db_user.user.username for db_user in db_users
    }
    assert {user["email"] for user in users} == {
        db_user.user.email for db_user in db_users
    }


# def test_create_new_user():
#     user_id = "new_user"
#     create_params = {
#         "id": user_id,
#     }
#     test_client = TestClient(app)
#     lower_bound = datetime.now()
#     upper_bound = lower_bound + timedelta(seconds=5)
#     response = test_client.post("/users", json=create_params)
#     assert response.status_code == 200

#     # Verify json keys in response
#     data = response.json()
#     assert "user" in data
#     user = data["user"]
#     assert "id" in user
#     assert user["id"] == user_id
#     assert "created_at" in user

#     # Verify creation date is within 5 second window of post
#     assert lower_bound <= datetime.fromisoformat(user["created_at"]) <= upper_bound

#     # Verify post response matches get response for the new user
#     response = test_client.get(f"/users/{user_id}")
#     assert response.status_code == 200
#     assert response.json() == data


# def test_create_duplicate_user():
#     # Known user in fake_db.json
#     user_id = "bishop"
#     create_params = {
#         "id": user_id,
#     }
#     test_client = TestClient(app)
#     response = test_client.post("/users", json=create_params)
#     assert response.status_code == 422

#     # Verify json keys in response
#     data = response.json()
#     assert "detail" in data
#     detail = data["detail"]
#     assert "type" in detail
#     assert detail["type"] == "duplicate_entity"
#     assert "entity_name" in detail
#     assert detail["entity_name"] == "User"
#     assert "entity_id" in detail
#     assert detail["entity_id"] == user_id


def test_get_user(client, user_fixture):
    db_user = user_fixture()
    response = client.get(f"/users/{db_user.user.id}")
    assert response.status_code == 200

    data = response.json()
    user = data["user"]
    
    assert user["username"] == db_user.user.username
    assert user["email"] == db_user.user.email




def test_get_invalid_user(client):
    user_id = 42069
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "User"
    assert "entity_id" in detail
    assert detail["entity_id"] == user_id


def test_get_user_chats():
    # Known user in fake_db.json
    user_id = "ripley"
    test_client = TestClient(app)
    response = test_client.get(f"/users/{user_id}/chats")
    assert response.status_code == 200

    data = response.json()
    assert "meta" in data
    assert "chats" in data
    meta = data["meta"]
    chats = data["chats"]
    assert "count" in meta
    assert meta["count"] == len(chats)
    assert "id" in chats[0]
    assert "name" in chats[0]
    assert "user_ids" in chats[0]
    assert "owner_id" in chats[0]
    assert "created_at" in chats[0]
    assert chats == sorted(chats, key=lambda chat: chat["name"])

    # This will error if an invalid iso datetime was received
    datetime.fromisoformat(chats[0]["created_at"])


def test_get_invalid_user_chats(client):
    user_id = 42069
    response = client.get(f"/users/{user_id}/chats")
    assert response.status_code == 404

    # Verify json keys in response
    data = response.json()
    assert "detail" in data
    detail = data["detail"]
    assert "type" in detail
    assert detail["type"] == "entity_not_found"
    assert "entity_name" in detail
    assert detail["entity_name"] == "User"
    assert "entity_id" in detail
    assert detail["entity_id"] == user_id

