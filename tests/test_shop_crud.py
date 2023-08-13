from test_user_crud import client, create_user, delete_user, get_headers

from shop.database import TestingSessionLocal
from shop.models import Shop


def test_patch_shop_success(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data = {"shop_name": fake.company(), "description": "PATCHED_DESCRIPTION"}
    response = client.patch(f"shop/", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    delete_user(new_user)


def test_patch_shop_not_changed(random_user_data, random_user_data_shop, fake):
    random_user_data["role"] = "SHOP"
    description = random_user_data_shop["description"]
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    db = TestingSessionLocal()
    shop = db.query(Shop).filter(Shop.user_id == user_id).first()
    data = {
        "description": shop.description,
    }
    response = client.patch(f"shop/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_user)


def test_patch_shop_name_taken(random_user_data, fake):
    random_user_data["role"] = "SHOP"
    new_user_1 = create_user(random_user_data)
    random_user_data_2 = random_user_data.copy()
    random_user_data_2["email"] = fake.email()
    random_user_data_2["username"] = fake.user_name()
    random_user_data_2["shop_name"] = fake.company()
    new_user_2 = create_user(random_user_data_2)
    assert new_user_1.status_code == 200
    assert new_user_2.status_code == 200
    user_id = new_user_2.json()["id"]
    data = {
        "shop_name": random_user_data["shop_name"],
        "description": "PATCHED_DESCRIPTION",
    }
    response = client.patch(f"shop/", headers=get_headers(user_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": "Shop name is already taken."}
    delete_user(new_user_1)
    delete_user(new_user_2)


def test_patch_shop_non_existing_field(random_user_data, random_user_data_shop, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "qwerty": "qwerty",
    }
    response = client.patch(f"shop/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(new_user)


def test_patch_shop_not_auth(random_user_data):
    data = {
        "shop_name": "TEST_SHOP_NAME",
        "description": "TEST_DESCRIPTION",
    }
    response = client.patch(f"shop/", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_shop_details(random_user_data, random_user_data_shop, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    data = {
        "shop_name": random_user_data_shop["shop_name"],
        "description": random_user_data_shop["description"],
    }
    response_patch = client.patch(f"shop/", headers=get_headers(user_id), json=data)
    assert response_patch.status_code == 200
    response = client.get(f"shop/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()["shop_name"] == random_user_data_shop["shop_name"]
    assert response.json()["description"] == random_user_data_shop["description"]
    delete_user(new_user)
