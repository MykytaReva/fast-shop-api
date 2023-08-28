from tests.conftest import (
    client,
    delete_user,
    get_amount_of_all_items,
    get_amount_of_items_per_shop,
    get_headers,
    get_shop_by_user_id,
)
from tests.factories import ShopFactory


def test_create_item_success(fake):
    user_data_dict = ShopFactory.create()

    new_shop = user_data_dict["new_shop"]
    category_id = user_data_dict["category_id"]
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


def test_create_item_name_is_taken(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_id = user_data_dict["category_id"]
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


def test_create_item_not_all_fields_provided(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {
        "image": fake.image_url(),
        "price": fake.pyint(),
    }
    response = client.post(f"/item/", headers=get_headers(user_id), json=data)
    assert response.status_code == 422
    delete_user(new_shop)


def test_create_item_unrecognized_field(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_id = user_data_dict["category_id"]
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
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"
    delete_user(new_shop)


def test_create_item_not_shop_role(fake):
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
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


def test_patch_item_success(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    data = {"name": fake.name(), "image": fake.image_url()}
    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json=data)
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]
    assert response.json()["image"] == data["image"]
    delete_user(new_shop)


def test_patch_item_name_is_taken(random_item_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    category_id = user_data_dict["category_id"]
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


def test_patch_item_no_changes_detected():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={})
    assert response.status_code == 422
    assert response.json() == {"detail": "Model was not changed."}
    delete_user(new_shop)


def test_patch_item_unrecognized_field():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.patch(f"/item/{item_slug}", headers=get_headers(user_id), json={"qwerty": "qwerty"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"
    delete_user(new_shop)


def test_delete_item_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.delete(f"/item/{item_slug}", headers=get_headers(user_id))
    assert response.status_code == 200
    delete_user(new_shop)


def test_delete_item_not_found(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    user_id = new_shop.json()["id"]

    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_shop)


def test_delete_item_not_shop_role(fake):
    user_data_dict = ShopFactory.create(role="CUSTOMER")
    new_user = user_data_dict["new_user"]
    assert new_user.status_code == 200

    user_id = new_user.json()["id"]
    response = client.delete(f"/item/{fake.slug()}", headers=get_headers(user_id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}
    delete_user(new_user)


def test_delete_item_not_shop_owner():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    item_slug_1 = user_data_dict_1["item_slug"]
    assert new_shop_1.status_code == 200

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    assert new_shop_2.status_code == 200
    user_id_2 = new_shop_2.json()["id"]

    response = client.delete(f"/item/{item_slug_1}", headers=get_headers(user_id_2))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}
    delete_user(new_shop_1)
    delete_user(new_shop_2)


def test_get_item_success():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    item_slug_1 = user_data_dict_1["item_slug"]

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    user_id_2 = new_shop_2.json()["id"]

    response = client.get(f"/item/{item_slug_1}", headers=get_headers(user_id_2))
    assert response.status_code == 200
    delete_user(new_shop_2)
    delete_user(new_shop_1)


def test_get_item_404():
    response = client.get("/item/fake-slug/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}


def test_get_all_items_success():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    assert new_shop_1.status_code == 200

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    assert new_shop_2.status_code == 200

    response = client.get("/items/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    delete_user(new_shop_2)
    delete_user(new_shop_1)


def test_get_items_by_shop_slug_success():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    user_id_1 = new_shop_1.json()["id"]
    shop_1 = get_shop_by_user_id(user_id_1)

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    user_id_2 = new_shop_2.json()["id"]
    shop_2 = get_shop_by_user_id(user_id_2)

    response_1 = client.get(f"/items/?shop={shop_1.slug}")
    response_2 = client.get(f"/items/?shop={shop_2.slug}")
    delete_user(new_shop_1)
    delete_user(new_shop_2)

    assert response_1.status_code == 200
    assert len(response_1.json()) == 1
    assert response_2.status_code == 200
    assert len(response_2.json()) == 1


def test_get_items_by_category_success():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    category_name = user_data_dict_1["category_name"]

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]

    response = client.get(f"/items/?category={category_name}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    delete_user(new_shop_2)
    delete_user(new_shop_1)


def test_get_items_by_shop_category_success():
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    category_name_1 = user_data_dict_1["category_name"]
    user_id_1 = new_shop_1.json()["id"]
    shop_1 = get_shop_by_user_id(user_id_1)

    user_data_dict_2 = ShopFactory.create()
    new_shop_2 = user_data_dict_2["new_shop"]
    category_name_2 = user_data_dict_2["category_name"]
    user_id_2 = new_shop_2.json()["id"]
    shop_2 = get_shop_by_user_id(user_id_2)

    response_1 = client.get(f"/items/?shop={shop_1.slug}&category={category_name_1}")
    response_2 = client.get(f"/items/?shop={shop_2.slug}&category={category_name_2}")

    assert response_1.status_code == 200
    assert len(response_1.json()) == 1
    assert response_2.status_code == 200
    assert len(response_2.json()) == 1
    delete_user(new_shop_1)
    delete_user(new_shop_2)


def test_get_items_by_shop_not_exists():
    user_data_dict_1 = ShopFactory.create()
    new_shop = user_data_dict_1["new_shop"]
    response = client.get(f"/items/?shop=fake-slug")
    assert response.status_code == 200
    assert len(response.json()) == get_amount_of_all_items()
    delete_user(new_shop)


def test_get_items_by_category_not_exists():
    user_data_dict_1 = ShopFactory.create()
    new_shop = user_data_dict_1["new_shop"]
    response = client.get(f"/items/?category=fake-category")
    assert response.status_code == 200
    assert len(response.json()) == get_amount_of_all_items()
    delete_user(new_shop)


def test_get_items_by_shop_exists_category_not(random_item_data):
    user_data_dict_1 = ShopFactory.create()
    new_shop = user_data_dict_1["new_shop"]
    user_id = new_shop.json()["id"]
    shop = get_shop_by_user_id(user_id)
    response = client.get(f"/items/?shop={shop.slug}&category=incorrect-category")

    assert response.status_code == 200
    assert len(response.json()) == get_amount_of_items_per_shop(user_id)
    delete_user(new_shop)


def test_get_items_by_shop_not_exists_category_exists():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_name = user_data_dict["category_name"]

    response = client.get(f"/items/?shop=fake-slug&category={category_name}")
    assert response.status_code == 200
    assert len(response.json()) == get_amount_of_all_items()
    delete_user(new_shop)
