from conftest import client, delete_user, get_headers, get_shop_by_shop_id

from tests.factories import ShopFactory


def test_patch_shop_success(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {"shop_name": fake.company(), "description": "PATCHED_DESCRIPTION"}
    response = client.patch(f"shop/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 200
    delete_user(new_shop)


def test_patch_shop_not_changed():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    shop = get_shop_by_shop_id(shop_id)
    data = {
        "description": shop.description,
    }
    response = client.patch(f"shop/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_shop)


def test_patch_shop_name_taken():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    assert new_shop_1.status_code == 200
    shop_id_1 = new_shop_1.json()["id"]

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    assert new_shop_1.status_code == 200
    shop_id_2 = new_shop_2.json()["id"]

    shop_name = get_shop_by_shop_id(shop_id_1).shop_name
    data = {
        "shop_name": shop_name,
        "description": "PATCHED_DESCRIPTION",
    }
    response = client.patch(f"shop/", headers=get_headers(shop_id_2), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": "Shop name is already taken."}
    delete_user(new_shop_1)
    delete_user(new_shop_2)


def test_patch_shop_non_existing_field():
    user_data_dict_1 = ShopFactory.create()
    new_shop = user_data_dict_1["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {
        "qwerty": "qwerty",
    }
    response = client.patch(f"shop/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"
    delete_user(new_shop)


def test_patch_shop_not_auth():
    data = {
        "shop_name": "TEST_SHOP_NAME",
        "description": "TEST_DESCRIPTION",
    }
    response = client.patch(f"shop/", json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_shop_details():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    shop_slug = get_shop_by_shop_id(shop_id).slug
    response = client.get(f"shop/{shop_slug}/")
    assert response.status_code == 200
    delete_user(new_shop)


def test_get_shop_404():
    response = client.get("shop/fake-slug/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Shop not found."}
