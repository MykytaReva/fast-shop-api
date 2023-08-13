from test_user_crud import client, create_user, delete_user, get_headers

from shop.database import TestingSessionLocal
from shop.models import Shop


def test_create_item_success(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }
    response_category = client.post(f"category/", headers=get_headers(user_id), json=category_data)
    assert response_category.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": response_category.json()["id"],
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    delete_user(new_user)


def test_create_item_name_is_taken(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }
    response_category = client.post(f"category/", headers=get_headers(user_id), json=category_data)
    assert response_category.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": response_category.json()["id"],
    }
    response_1 = client.post(f"/item/", headers=get_headers(user_id), json=data)
    response_2 = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response_1.status_code == 200
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": f"You already have item with the name '{data['name']}'."}
    delete_user(new_user)


def test_create_item_not_all_fields_provided(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }
    response_category = client.post(f"category/", headers=get_headers(user_id), json=category_data)
    assert response_category.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    delete_user(new_user)


def test_create_item_unrecognized_field(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }
    response_category = client.post(f"category/", headers=get_headers(user_id), json=category_data)
    assert response_category.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": response_category.json()["id"],
        "qwerty": "qwerty",
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(new_user)
