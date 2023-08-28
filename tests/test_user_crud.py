from conftest import client, create_user, delete_user, ger_user_by_id_approve, get_headers

from shop import models
from shop.database import test_engine
from tests.factories import ShopFactory

# Create all tables in the database (if they don't exist)
models.Base.metadata.create_all(bind=test_engine)


def test_read_users_me_authenticated_user_success(random_user_data):
    new_user = create_user(random_user_data)
    ger_user_by_id_approve(new_user.json()["id"])
    data = {"username": random_user_data["email"], "password": random_user_data["password"]}
    response = client.post("/login", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()

    # Make a GET request to the /me endpoint with the access token in the Authorization header
    headers = {"Authorization": f"Bearer {response.json().get('access_token')}"}
    response_me = client.get("/me", headers=headers)

    # Assert that the response is successful and contains the user data
    assert response_me.status_code == 200
    assert response_me.json()["email"] == new_user.json()["email"]
    delete_user(new_user)


def test_read_users_me_authenticated_user_fail(random_user_data):
    new_user = create_user(random_user_data)
    data = {"username": random_user_data["email"], "password": random_user_data["password"]}
    response = client.post("/login", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()

    # Make a GET request to the /me endpoint with the access token in the Authorization header
    headers = {"Authorization": f"Bearer NO-TOKEN"}
    response_me = client.get("/me", headers=headers)

    # Assert that the response is successful and contains the user data
    assert response_me.status_code == 401
    assert response_me.json() == {"detail": "Could not validate credentials"}
    delete_user(new_user)


def test_get_index_page():
    response = client.get("/")
    assert response.status_code == 200


def test_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200


def test_get_user_by_id_success():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    response = client.get(f"/user/{user_id}/")
    assert response.status_code == 200
    delete_user(response)


def test_get_user_by_id_404():
    user_id = 999999
    response = client.get(f"/user/{user_id}/")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_delete_user_success():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    response = client.delete("/user/", headers=get_headers(user_id))

    assert response.status_code == 200

    assert response.json() == {"message": "User deleted successfully."}


def test_delete_user_not_auth():
    response = client.delete("/user/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_patch_user_success(fake):
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "first_name": "PATCHED_NAME",
        "last_name": "PATCHED_NAME",
        "username": fake.user_name(),
        "city": "PATCHED_CITY",
        "country": "PATCHED_DOB",
    }
    response = client.patch(f"user/", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    delete_user(new_user)


def test_patch_user_no_changes_detected():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    response = client.patch(f"user/", headers=get_headers(user_id), json={})
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_user)


def test_patch_user_username_taken(random_user_data, fake):
    new_user_1 = create_user(random_user_data)
    ger_user_by_id_approve(new_user_1.json()["id"])
    random_user_data["email"] = fake.email()
    random_user_data["username"] = fake.user_name()
    new_user_2 = create_user(random_user_data)
    ger_user_by_id_approve(new_user_2.json()["id"])
    assert new_user_1.status_code == 200
    assert new_user_2.status_code == 200

    data = {"username": new_user_2.json().get("username")}
    user_id = new_user_1.json()["id"]
    response = client.patch(f"user/", headers=get_headers(user_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": "Username is already taken."}
    delete_user(new_user_1)
    delete_user(new_user_2)


def test_patch_user_not_auth():
    data = {"username": "TEST_USERNAME"}
    response = client.patch(f"user/", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
