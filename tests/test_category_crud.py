from test_user_crud import client, create_user, delete_user, get_headers


def test_category_create_success(new_shop, fake):
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]
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
    delete_user(new_shop)


def test_category_name_taken(new_shop_with_category, fake):
    new_shop = new_shop_with_category["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {
        "name": "fixture-category",
    }
    response = client.post(f"category/", headers=get_headers(shop_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": f"You already have category with the name '{data['name']}'."}
    delete_user(new_shop)


def test_category_name_not_provided(new_shop, fake):
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    data_1 = {
        "is_available": False,
    }
    response_1 = client.post(f"category/", headers=get_headers(shop_id), json=data_1)
    assert response_1.status_code == 422

    data_1 = {
        "name": "string",
    }
    response_2 = client.post(f"category/", headers=get_headers(shop_id), json=data_1)
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "Category name was not provided."}
    delete_user(new_shop)


def test_category_delete_success(new_shop_with_category):
    new_shop = new_shop_with_category["new_shop"]
    category_slug = new_shop_with_category["category_slug"]
    assert new_shop.status_code == 200

    shop_id = new_shop.json()["id"]

    response = client.delete(f"category/{category_slug}/", headers=get_headers(shop_id))
    assert response.status_code == 200

    delete_user(new_shop)


def test_category_delete_404(new_shop_with_category):
    new_shop = new_shop_with_category["new_shop"]
    assert new_shop.status_code == 200

    user_id = new_shop.json()["id"]
    patched_slug = "not-existing-slug"

    response_delete_3 = client.delete(f"category/{patched_slug}/", headers=get_headers(user_id))
    assert response_delete_3.status_code == 404
    assert response_delete_3.json() == {"detail": "Category not found."}

    delete_user(new_shop)


def test_category_patch_name_is_taken(new_shop_with_category, fake):
    new_shop = new_shop_with_category["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]
    data = {
        "name": f"{fake.company()}-category",
    }

    response = client.post(f"category/", headers=get_headers(user_id), json=data)
    assert response.status_code == 200

    response_patch_2 = client.patch(
        f"category/{response.json()['slug']}/", headers=get_headers(user_id), json={"name": "fixture-category"}
    )
    assert response_patch_2.status_code == 409
    assert response_patch_2.json() == {"detail": f"You already have category with the name 'fixture-category'."}

    delete_user(new_shop)


def test_category_patch_success(new_shop_with_category, fake):
    new_shop = new_shop_with_category["new_shop"]
    category_slug = new_shop_with_category["category_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(user_id), json={"name": "patched_category_name"}
    )
    assert response_patch.status_code == 200
    assert response_patch.json()["name"] == "patched_category_name"

    delete_user(new_shop)


def test_category_patch_404(new_shop_with_category):
    new_shop = new_shop_with_category["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    patched_slug = "not-existing-slug"
    response_patch = client.patch(
        f"category/{patched_slug}/", headers=get_headers(user_id), json={"name": "patched_category_name"}
    )
    assert response_patch.status_code == 404
    assert response_patch.json() == {"detail": "Category not found."}
    delete_user(new_shop)


def test_category_patch_unrecognized_field(new_shop_with_category):
    new_shop = new_shop_with_category["new_shop"]
    category_slug = new_shop_with_category["category_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(user_id), json={"qwerty": "patched_category_name"}
    )
    assert response_patch.status_code == 422
    assert response_patch.json() == {"detail": "Unrecognized field: qwerty"}
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


def test_category_patch_no_changes_detected(new_shop_with_category):
    new_shop = new_shop_with_category["new_shop"]
    category_slug = new_shop_with_category["category_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response_patch = client.patch(
        f"category/{category_slug}/", headers=get_headers(user_id), json={"name": "fixture-category"}
    )
    assert response_patch.status_code == 422
    assert response_patch.json() == {"detail": "Model was not changed."}

    delete_user(new_shop)
