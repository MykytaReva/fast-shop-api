from tests.conftest import client, delete_user, get_headers
from tests.factories import ShopFactory


def test_category_create_success(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    data = {
        "name": f"{fake.company()}-category",
    }
    response = client.post(f"category/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 200
    delete_user(new_shop)


def test_category_name_taken():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {
        "name": "fixture-category",
    }
    response = client.post(f"category/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": f"You already have category with the name '{data['name']}'."}
    delete_user(new_shop)


def test_category_name_not_provided():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    data_1 = {
        "is_available": False,
    }
    response_1 = client.post(f"category/", headers=get_headers(shop_id), json=data_1)
    assert response_1.status_code == 422

    data_2 = {
        "name": "string",
    }
    response_2 = client.post(f"category/", headers=get_headers(shop_id), json=data_2)
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "Category name was not provided."}
    delete_user(new_shop)


def test_category_delete_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_slug = user_data_dict["category_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response = client.delete(f"category/{category_slug}/", headers=get_headers(shop_id))
    assert response.status_code == 200
    delete_user(new_shop)


def test_category_delete_404(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response_delete_3 = client.delete(f"category/{fake.slug()}/", headers=get_headers(shop_id))
    assert response_delete_3.status_code == 404
    assert response_delete_3.json() == {"detail": "Category not found."}
    delete_user(new_shop)


def test_category_patch_name_is_taken(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {
        "name": f"{fake.company()}-category",
    }

    response = client.post(f"category/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 200

    response_patch_2 = client.patch(
        f"category/{response.json()['slug']}/", headers=get_headers(shop_id), json={"name": "fixture-category"}
    )
    assert response_patch_2.status_code == 409
    assert response_patch_2.json() == {"detail": f"You already have category with the name 'fixture-category'."}
    delete_user(new_shop)


def test_category_patch_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_slug = user_data_dict["category_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(shop_id), json={"name": "patched_category_name"}
    )
    assert response_patch.status_code == 200
    assert response_patch.json()["name"] == "patched_category_name"
    delete_user(new_shop)


def test_category_patch_404(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{fake.slug()}/", headers=get_headers(shop_id), json={"name": "patched_category_name"}
    )
    assert response_patch.status_code == 404
    assert response_patch.json() == {"detail": "Category not found."}
    delete_user(new_shop)


def test_category_patch_unrecognized_field():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_slug = user_data_dict["category_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(shop_id), json={"qwerty": "patched_category_name"}
    )
    assert response_patch.status_code == 422
    assert response_patch.json()["detail"][0]["msg"] == "Extra inputs are not permitted"
    delete_user(new_shop)


def test_category_patch_cannot_validate_credentials(fake):
    data = {
        "name": f"{fake.company()}-category",
    }
    response = client.post(f"category/", headers=get_headers(999999), json=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_category_patch_not_auth():
    response = client.post(f"category/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_category_patch_no_changes_detected():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_slug = user_data_dict["category_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(shop_id), json={"name": "fixture-category"}
    )
    assert response_patch.status_code == 422
    assert response_patch.json() == {"detail": "Model was not changed."}
    delete_user(new_shop)
