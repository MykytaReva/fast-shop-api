from test_user_crud import client, create_user, delete_user, get_headers


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


def test_create_item_not_shop_role(random_user_data, fake):
    random_user_data["role"] = "CUSTOMER"
    new_user = create_user(random_user_data)
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


def test_patch_item_success(random_user_data, random_item_data, fake):
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
    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert response.status_code == 200

    item_slug = response.json()["slug"]
    data = {"name": fake.name(), "image": fake.image_url()}
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]
    assert response.json()["image"] == data["image"]
    delete_user(new_user)


def test_patch_item_name_is_taken(random_user_data, random_item_data, fake):
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
    random_item_data["category_id"] = response_category.json()["id"]
    response_1 = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    random_item_data["name"] = fake.name()
    response_2 = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert response_1.status_code == 200
    assert response_2.status_code == 200

    item_slug = response_1.json()["slug"]
    data = {
        "name": random_item_data["name"],
    }
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json=data)
    assert response.status_code == 409
    assert response.json() == {"detail": f"You already have item with the name '{data['name']}'."}
    delete_user(new_user)


def test_patch_item_no_changes_detected(random_user_data, random_item_data, fake):
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
    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert response.status_code == 200
    item_slug = response.json()["slug"]
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={})
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_user)


def test_patch_item_unrecognized_field(random_user_data, random_item_data, fake):
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
    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert response.status_code == 200
    item_slug = response.json()["slug"]
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={"qwerty": "qwerty"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Unrecognized field: qwerty"}
    delete_user(new_user)


def test_delete_item_success(random_user_data, random_item_data, fake):
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
    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(user_id), json=random_item_data)
    assert response.status_code == 200

    item_slug = response.json()["slug"]
    response = client.delete(f"/item/{item_slug}", headers=get_headers(user_id))
    assert response.status_code == 200
    delete_user(new_user)


def test_delete_item_not_found(random_user_data, random_item_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200

    user_id = new_user.json()["id"]
    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_user)


def test_delete_item_not_shop_role(random_user_data, random_item_data, fake):
    random_user_data["role"] = "CUSTOMER"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200

    user_id = new_user.json()["id"]
    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}
    delete_user(new_user)


def test_delete_item_not_shop_owner(random_user_data, random_item_data, fake):
    random_user_data["role"] = "SHOP"
    new_user_1 = create_user(random_user_data)
    assert new_user_1.status_code == 200

    user_id_1 = new_user_1.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }

    response_category = client.post(f"category/", headers=get_headers(user_id_1), json=category_data)
    assert response_category.status_code == 200

    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(user_id_1), json=random_item_data)
    assert response.status_code == 200

    item_slug = response.json()["slug"]

    random_user_data["email"] = fake.email()
    random_user_data["username"] = fake.user_name()
    random_user_data["shop_name"] = fake.company()
    new_user_2 = create_user(random_user_data)
    assert new_user_2.status_code == 200

    user_id_2 = new_user_2.json()["id"]
    response = client.delete(f"/item/{item_slug}", headers=get_headers(user_id_2))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_user_2)


def test_get_item_success(random_user_data, random_item_data, fake):
    random_user_data["role"] = "SHOP"
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200

    shop_id = new_user.json()["id"]
    category_data = {
        "name": f"{fake.company()}-category",
    }

    response_category = client.post(f"category/", headers=get_headers(shop_id), json=category_data)
    assert response_category.status_code == 200

    random_item_data["category_id"] = response_category.json()["id"]
    response = client.post(f"/item/", headers=get_headers(shop_id), json=random_item_data)
    assert response.status_code == 200

    item_slug = response.json()["slug"]

    random_user_data["role"] = "CUSTOMER"
    random_user_data["email"] = fake.email()
    random_user_data["username"] = fake.user_name()

    new_user = create_user(random_user_data)
    user_id = new_user.json()["id"]
    response = client.get(f"/item/{item_slug}", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()["name"] == random_item_data["name"]
    assert response.json()["image"] == random_item_data["image"]
    delete_user(new_user)


def test_get_item_404(random_user_data, random_item_data, fake):
    response = client.get("/item/fake-slug/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
