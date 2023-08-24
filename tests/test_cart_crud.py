from conftest import client, create_user, delete_user, get_headers


def test_cart_add_success(random_user_data, fake):
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
    item_slug = response.json()["slug"]
    response = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response.status_code == 200


def test_cart_add_item_not_found(random_user_data, fake):
    new_user = create_user(random_user_data)
    assert new_user.status_code == 200
    user_id = new_user.json()["id"]
    response = client.post(f"/add-to-the-cart/{fake.slug()}/", headers=get_headers(user_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}


def test_cart_subtract_success(random_user_data, fake):
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
    item_slug = response.json()["slug"]
    data = {"quantity": 2}
    response_add = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id), json=data)
    assert response_add.status_code == 200
    response = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response.status_code == 200


def test_cart_subtract_removed(random_user_data, fake):
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
    item_slug = response.json()["slug"]
    response_add = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id), json=data)
    assert response_add.status_code == 200
    response_1 = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_1.json() == {"detail": "Item removed from the cart."}
    response_2 = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_2.json() == {"detail": "Item already removed from the cart."}


def test_cart_get_all_items(random_user_data, fake):
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
    item_slug = response.json()["slug"]
    response = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response.status_code == 200

    response_cart = client.get(f"/cart/", headers=get_headers(user_id))
    response_cart.status_code == 200
