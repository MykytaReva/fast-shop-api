from test_user_crud import client, create_user, delete_user, get_headers

from shop.database import TestingSessionLocal
from shop.models import Shop


def test_category_create_success(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data_1 = {
        "name": f"{fake.company()}-category",
    }
    data_2 = {
        "name": f"{fake.company()}-category",
    }
    response_1 = client.post(f"category/", headers=get_headers(user_id), json=data_1)
    response_2 = client.post(f"category/", headers=get_headers(user_id), json=data_2)
    assert response_1.status_code == 200
    assert response_2.status_code == 200

    delete_user(new_user)


def test_category_name_taken(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data_1 = {
        "name": f"{fake.company()}-category",
    }
    data_2 = {
        "name": f"{fake.company()}-category",
    }
    response_1 = client.post(f"category/", headers=get_headers(user_id), json=data_1)
    response_2 = client.post(f"category/", headers=get_headers(user_id), json=data_2)
    assert response_1.status_code == 200
    assert response_2.status_code == 200

    response_3 = client.post(f"category/", headers=get_headers(user_id), json=data_2)
    assert response_3.status_code == 409
    assert response_3.json() == {"detail": f"You already have category with the name '{data_2['name']}'."}
    delete_user(new_user)


def test_category_name_not_provided(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]

    data_1 = {
        "is_available": False,
    }
    response_1 = client.post(f"category/", headers=get_headers(user_id), json=data_1)
    assert response_1.status_code == 422

    data_1 = {
        "name": "string",
    }
    response_2 = client.post(f"category/", headers=get_headers(user_id), json=data_1)
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "Category name was not provided."}
    delete_user(new_user)
