from test_user_crud import client, create_user, delete_user


def test_login_success(db, random_user_data):
    new_user = create_user(random_user_data)
    # data = {
    #     'username': new_user.json().get('username'),
    #     'password': new_user.json().get('password')}
    data = {"username": random_user_data["email"], "password": random_user_data["password"]}
    response = client.post("/login", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    delete_user(new_user)


def test_login_invalid_details(db, random_user_data):
    new_user = create_user(random_user_data)
    # data = {
    #     'username': new_user.json().get('username'),
    #     'password': new_user.json().get('password')}
    data = {"username": random_user_data["email"], "password": "WRONG_PASSWORD"}
    response = client.post("/login", data=data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect credentials."}
    delete_user(new_user)


def test_login_user_not_found(db, random_user_data):
    data = {"username": random_user_data["email"], "password": "WRONG_PASSWORD"}
    response = client.post("/login", data=data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect credentials."}


def test_create_user_success(db, random_user_data):
    data = random_user_data
    response = create_user(data)
    assert response.status_code == 200
    assert response.json()["username"] == data["username"]
    assert response.json()["email"] == data["email"]
    delete_user(response)


def test_create_user_not_all_fields_provided(db, random_user_data):
    data = random_user_data.pop("username")
    response = create_user(data)
    assert response.status_code == 422
    delete_user(response)


def test_create_user_non_existing_field(db, random_user_data):
    random_user_data["qwerty"] = "qwerty"
    data = random_user_data
    response = create_user(data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(response)


def test_create_user_incorrect_role(db, random_user_data):
    random_user_data["role"] = "INCORRECT_ROLE"
    response = create_user(random_user_data)
    assert response.status_code == 422
    delete_user(response)


def test_create_user_email_taken(db, random_user_data):
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


def test_create_user_username_taken(db, random_user_data, fake):
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
