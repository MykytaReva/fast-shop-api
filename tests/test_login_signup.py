from datetime import datetime, timedelta

from conftest import client, create_user, delete_user
from jose import jwt

from shop import constants
from tests.factories import ShopFactory


def test_login_success(random_user_data):
    new_user = create_user(random_user_data)
    data = {"username": random_user_data["email"], "password": random_user_data["password"]}
    response = client.post("/login", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    delete_user(new_user)


def test_login_invalid_details(random_user_data):
    new_user = create_user(random_user_data)
    data = {"username": random_user_data["email"], "password": "WRONG_PASSWORD"}
    response = client.post("/login", data=data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect credentials."}
    delete_user(new_user)


def test_login_user_not_found(random_user_data):
    data = {"username": random_user_data["email"], "password": "WRONG_PASSWORD"}
    response = client.post("/login", data=data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect credentials."}


def test_create_user_success(random_user_data):
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    delete_user(new_user)


def test_create_user_not_all_fields_provided(random_user_data):
    data = random_user_data.pop("username")
    response = create_user(data)
    assert response.status_code == 422
    delete_user(response)


def test_create_user_non_existing_field(random_user_data):
    random_user_data["qwerty"] = "qwerty"
    data = random_user_data
    response = create_user(data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"
    delete_user(response)


def test_create_user_incorrect_role(random_user_data):
    random_user_data["role"] = "INCORRECT_ROLE"
    response = create_user(random_user_data)
    assert response.status_code == 422
    delete_user(response)


def test_create_user_email_taken(random_user_data):
    data1 = random_user_data
    user_1 = create_user(data1)  # Create the first user
    assert user_1.status_code == 200

    # Create another user with a different username but the same email
    data2 = random_user_data.copy()
    data2["email"] = data1["email"]

    user2 = create_user(data2)
    assert user2.status_code == 409
    assert user2.json() == {"detail": "Email is already taken."}
    delete_user(user_1)


def test_create_user_username_taken(random_user_data, fake):
    data1 = random_user_data
    user_1 = create_user(data1)  # Create the first user
    assert user_1.status_code == 200

    # Create another user with the same username
    data2 = random_user_data.copy()
    data2["email"] = fake.email()
    data2["username"] = data1["username"]

    user_2 = create_user(data2)
    assert user_2.status_code == 409
    assert user_2.json() == {"detail": "Username is already taken."}
    delete_user(user_1)
    delete_user(user_2)


def test_email_verification_success():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    token = jwt.encode({"sub": str(user_id)}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    response = client.get(f"/verification/?token={token}")
    assert response.status_code == 200
    delete_user(new_user)


def test_email_verification_invalid_token():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    token = jwt.encode({"sub": str(user_id)}, "INCORRECT_SECRET", algorithm=constants.ALGORITHM)
    response = client.get(f"/verification/?token={token}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}
    delete_user(new_user)


def test_email_verification_expired_token():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    # Generate token with a future expiration time for the first verification
    future_expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(user_id), "exp": future_expiration}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
    )
    response = client.get(f"/verification/?token={token}")
    assert response.status_code == 200
    # Generate token with a past expiration time for the second verification
    past_expiration = datetime.utcnow() - timedelta(hours=1)
    exp_token = jwt.encode(
        {"sub": str(user_id), "exp": past_expiration}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
    )
    response = client.get(f"/verification/?token={exp_token}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}
    delete_user(new_user)


def test_reset_password_success():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    token = jwt.encode({"sub": str(user_id)}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    data = {"new_password": "qwertyqwerty"}
    response = client.post(f"/reset-password/verify/?token={token}", json=data)
    assert response.status_code == 200
    assert response.json() == {"detail": "Password has been changed."}
    delete_user(new_user)


def test_reset_password_invalid_token():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    token = jwt.encode({"sub": str(user_id)}, "INCORRECT_SECRET", algorithm=constants.ALGORITHM)
    data = {"new_password": "qwertyqwerty"}
    response = client.post(f"/reset-password/verify/?token={token}", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token."}
    delete_user(new_user)


def test_reset_password_user_not_found():
    token = jwt.encode({"sub": str(9999)}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    data = {"new_password": "qwertyqwerty"}
    response = client.post(f"/reset-password/verify/?token={token}", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_reset_password_expired_token():
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    # Generate token with a future expiration time for the first verification
    future_expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(user_id), "exp": future_expiration}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
    )
    data = {"new_password": "qwertyqwerty"}
    response = client.post(f"/reset-password/verify/?token={token}", json=data)
    assert response.status_code == 200
    # Generate token with a past expiration time for the second verification
    past_expiration = datetime.utcnow() - timedelta(hours=1)
    exp_token = jwt.encode(
        {"sub": str(user_id), "exp": past_expiration}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
    )
    response = client.post(f"/reset-password/verify/?token={exp_token}", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has expired."}
    delete_user(new_user)
