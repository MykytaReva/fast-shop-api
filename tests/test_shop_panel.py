from tests.conftest import client, create_order, delete_user, get_headers
from tests.factories import ShopFactory


def test_get_all_shop_category_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    category_id = user_data_dict["category_id"]
    category_slug = user_data_dict["category_slug"]
    shop_id = user_data_dict["shop_id"]
    user_id = new_shop.json()["id"]
    response = client.get("/shop-admin/categories/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()[0] == {
        "id": category_id,
        "is_available": True,
        "name": "fixture-category",
        "shop_id": shop_id,
        "slug": category_slug,
    }
    delete_user(new_shop)


def test_get_all_shop_category_empty():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    category_slug = user_data_dict["category_slug"]
    response_delete = client.delete(f"/category/{category_slug}/", headers=get_headers(user_id))
    assert response_delete.status_code == 200
    response = client.get("/shop-admin/categories/", headers=get_headers(user_id))
    assert response.status_code == 409
    assert response.json() == {"detail": "No categories found"}
    delete_user(new_shop)


def test_get_all_shop_items_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    category_slug = user_data_dict["category_slug"]
    response = client.get("/shop-admin/items/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()[0]["name"] == "fixture-item"
    delete_user(new_shop)


def test_get_all_shop_items_empty():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    item_slug = user_data_dict["item_slug"]
    response_delete = client.delete(f"/item/{item_slug}/", headers=get_headers(user_id))
    assert response_delete.status_code == 200
    response = client.get("/shop-admin/items/", headers=get_headers(user_id))
    assert response.status_code == 409
    assert response.json() == {"detail": "No items found"}
    delete_user(new_shop)


def test_get_all_shop_no_users():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    response = client.get("/shop-admin/users/", headers=get_headers(user_id))
    assert response.status_code == 409
    assert response.json() == {"detail": "No users have ordered in your shop."}
    delete_user(new_shop)


def test_get_all_shop_users(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    item_slug = user_data_dict["item_slug"]
    response_cart = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_cart.status_code == 200
    create_order(order_data, user_id)
    response = client.get("/shop-admin/users/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()[0]["id"] == user_id
    delete_user(new_shop)


def test_get_all_shop_orders_per_user(order_data):
    user_data_dict_1 = ShopFactory.create()
    new_shop_1 = user_data_dict_1["new_shop"]
    user_id_1 = new_shop_1.json()["id"]
    item_slug = user_data_dict_1["item_slug"]
    user_data_dict_2 = ShopFactory.create(role="CUSTOMER")
    new_shop_2 = user_data_dict_2["new_user"]
    user_id_2 = new_shop_2.json()["id"]
    response_cart = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id_2))
    assert response_cart.status_code == 200
    response_order = create_order(order_data, user_id_2)
    response = client.get(f"/shop-admin/users/{user_id_2}/", headers=get_headers(user_id_1))
    assert response.status_code == 200
    assert response.json()[0]["order_id"] == response_order.json()["id"]
    delete_user(new_shop_1)
    delete_user(new_shop_2)


def test_get_shop_stats_for_each_item(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    item_slug = user_data_dict["item_slug"]
    item_id = user_data_dict["item_id"]
    response_cart = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_cart.status_code == 200
    response_order = create_order(order_data, user_id)
    assert response_order.status_code == 200
    response_wish_list = client.post(f"/wish-list/{item_slug}/", headers=get_headers(user_id))
    assert response_wish_list.status_code == 200
    response = client.get("/shop-admin/stats-items/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()[str(item_id)]["price"] == response_order.json()["total_paid"]
    assert response.json()[str(item_id)]["wish_list_count"] == 1
    delete_user(new_shop)


def test_get_total_revenue_with_filtering(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    item_slug = user_data_dict["item_slug"]
    response_cart = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_cart.status_code == 200
    response_order = create_order(order_data, user_id)
    assert response_order.status_code == 200
    response = client.get(
        "/shop-admin/revenue/?start_date=2023-01-01&end_date=2024-09-01", headers=get_headers(user_id)
    )
    assert response.status_code == 200
    assert response.json()["Revenue"] == response_order.json()["total_paid"]
    delete_user(new_shop)


def test_get_total_revenue_without_filtering(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    item_slug = user_data_dict["item_slug"]
    response_cart = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(user_id))
    assert response_cart.status_code == 200
    response_order = create_order(order_data, user_id)
    assert response_order.status_code == 200
    response = client.get("/shop-admin/revenue/", headers=get_headers(user_id))
    assert response.status_code == 200
    assert response.json()["Total revenue"] == response_order.json()["total_paid"]
    delete_user(new_shop)
