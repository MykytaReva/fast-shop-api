from conftest import client, create_order, delete_user, get_headers, get_shop_order_by_order_id

from tests.factories import ShopFactory


def test_order_create_success(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    cart_response = user_data_dict["cart_response"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    assert response.json()["total_paid"] == cart_response.json()["price"] * cart_response.json()["quantity"]
    delete_user(new_shop)


def test_order_create_empty_cart(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    shop_id = new_shop.json()["id"]
    response_sub = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response_sub.status_code == 200
    response = create_order(order_data, shop_id)
    assert response.status_code == 409
    assert response.json() == {"detail": "Cart is empty."}
    delete_user(new_shop)


def test_order_create_not_all_data_provided(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    order_data.pop("phone_number")
    response = create_order(order_data, shop_id)
    assert response.status_code == 422
    delete_user(new_shop)


def test_shop_order_get_created_success(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    order_id = response.json()["id"]
    shop_order = get_shop_order_by_order_id(shop_id, order_id)
    response_shop = client.get(f"/shop-orders/{shop_order.id}", headers=get_headers(shop_id))
    assert response_shop.status_code == 200
    delete_user(new_shop)


def test_order_get_created_success(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    order_id = response.json()["id"]
    response_order = client.get(f"/orders/{order_id}", headers=get_headers(shop_id))
    assert response_order.status_code == 200
    delete_user(new_shop)


def test_order_get_orders_user(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    response_order = client.get("/orders/", headers=get_headers(shop_id))
    assert response_order.status_code == 200
    delete_user(new_shop)


def test_order_get_orders_shop(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    response_order = client.get("/shop-orders/", headers=get_headers(shop_id))
    assert response_order.status_code == 200
    delete_user(new_shop)


def test_order_get_no_orders_user(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    shop_id = new_shop.json()["id"]
    response_sub = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response_sub.status_code == 200
    response = client.get("/orders/", headers=get_headers(shop_id))
    assert response.status_code == 409
    assert response.json() == {"detail": "You have no orders yet."}
    delete_user(new_shop)


def test_order_get_no_orders_shop(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    shop_id = new_shop.json()["id"]
    response_sub = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response_sub.status_code == 200
    response = client.get("/shop-orders/", headers=get_headers(shop_id))
    assert response.status_code == 409
    assert response.json() == {"detail": "You have no orders yet."}
    delete_user(new_shop)


def test_order_get_not_found_user():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = client.get("/orders/999999", headers=get_headers(shop_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found."}
    delete_user(new_shop)


def test_order_get_not_found_shop():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = client.get("/shop-orders/999999", headers=get_headers(shop_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found."}
    delete_user(new_shop)


def test_shop_order_status_patch_success(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    order_id = response.json()["id"]
    shop_order = get_shop_order_by_order_id(shop_id, order_id)
    response_patch = client.patch(
        f"/shop-orders/{shop_order.id}/", headers=get_headers(shop_id), json={"status": "In Process"}
    )
    assert response_patch.status_code == 200
    delete_user(new_shop)


def test_shop_order_status_patch_no_valid_status(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    order_id = response.json()["id"]
    shop_order = get_shop_order_by_order_id(shop_id, order_id)
    response_patch = client.patch(
        f"/shop-orders/{shop_order.id}/", headers=get_headers(shop_id), json={"status": "STH WRONG"}
    )
    print(response_patch.json())
    assert response_patch.json()["detail"][0]["msg"] == "Input should be 'New','In Process' or 'Sent'"
    assert response_patch.status_code == 422
    delete_user(new_shop)


def test_order_patch_status_not_changed(order_data):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    shop_id = new_shop.json()["id"]
    response = create_order(order_data, shop_id)
    assert response.status_code == 200
    order_id = response.json()["id"]
    shop_order = get_shop_order_by_order_id(shop_id, order_id)
    response_patch = client.patch(
        f"/shop-orders/{shop_order.id}/", headers=get_headers(shop_id), json={"status": "New"}
    )
    assert response_patch.status_code == 422
    assert response_patch.json() == {"detail": "Model was not changed."}
    delete_user(new_shop)
