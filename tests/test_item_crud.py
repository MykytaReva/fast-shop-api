from tests.conftest import client, create_user, delete_user, get_headers


def test_create_item_success(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    category_id = new_shop_with_category_and_item["category_id"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]
    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": category_id,
    }
    response = client.post("/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    delete_user(new_shop)


def test_create_item_name_is_taken(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    category_id = new_shop_with_category_and_item["category_id"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {
        "name": "fixture-item",
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": category_id,
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": f"You already have item with the name '{data['name']}'."}
    delete_user(new_shop)


def test_create_item_not_all_fields_provided(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {
        "image": fake.image_url(),
        "price": fake.pyint(),
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    delete_user(new_shop)


def test_create_item_unrecognized_field(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    category_id = new_shop_with_category_and_item["category_id"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {
        "name": fake.name(),
        "image": fake.image_url(),
        "title": fake.text(),
        "description": fake.text(),
        "price": fake.pyint(),
        "category_id": category_id,
        "qwerty": "qwerty",
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(new_shop)


def test_create_item_not_shop_role(new_user, fake):
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    item_data = {
        "name": f"{fake.company()}-category",
        "category_id": 1,
    }
    response_category = client.post(f"item/", headers=get_headers(user_id), json=item_data)
    assert response_category.status_code == 403
    assert response_category.json() == {"detail": "Forbidden."}
    delete_user(new_user)


def test_patch_item_success(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {"name": fake.name(), "image": fake.image_url()}
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]
    assert response.json()["image"] == data["image"]
    delete_user(new_shop)


def test_patch_item_name_is_taken(new_shop_with_category_and_item, random_item_data):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    category_id = new_shop_with_category_and_item["category_id"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]
    random_item_data["category_id"] = category_id
    new_item = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert new_item.status_code == 200
    data = {"name": random_item_data["name"]}
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": f"You already have item with the name '{data['name']}'."}
    delete_user(new_shop)


def test_patch_item_no_changes_detected(new_shop_with_category_and_item):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={})
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_shop)


def test_patch_item_unrecognized_field(new_shop_with_category_and_item):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={"qwerty": "qwerty"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(new_shop)


def test_delete_item_success(new_shop_with_category_and_item):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.delete(f"/item/{item_slug}", headers=get_headers(user_id))
    assert response.status_code == 200
    delete_user(new_shop)


def test_delete_item_not_found(new_shop_with_category_and_item, fake):
    new_shop = new_shop_with_category_and_item["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_shop)


def test_delete_item_not_shop_role(new_user, fake):
    assert new_user.status_code == 200

    user_id = new_user.json()["id"]
    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}
    delete_user(new_user)


def test_delete_item_not_shop_owner(new_shop_with_category_and_item, random_second_user):
    new_shop_1 = new_shop_with_category_and_item["new_shop"]
    item_slug_1 = new_shop_with_category_and_item["item_slug"]
    assert new_shop_1.status_code == 200

    random_second_user["role"] = "SHOP"
    new_shop_2 = create_user(random_second_user)

    assert new_shop_2.status_code == 200
    user_id_2 = new_shop_2.json()["id"]

    response = client.delete(f"/item/{item_slug_1}", headers=get_headers(user_id_2))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_shop_1)
    delete_user(new_shop_2)


def test_get_item_success(new_shop_with_category_and_item, random_second_user):
    new_shop = new_shop_with_category_and_item["new_shop"]
    item_slug = new_shop_with_category_and_item["item_slug"]
    assert new_shop.status_code == 200

    new_user = create_user(random_second_user)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    response = client.get(f"/item/{item_slug}", headers=get_headers(user_id))
    assert response.status_code == 200
    delete_user(new_user)


def test_get_item_404():
    response = client.get("/item/fake-slug/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
