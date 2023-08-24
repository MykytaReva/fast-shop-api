from conftest import client, get_headers

from tests.factories import ShopFactory


def test_cart_add_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]

    response = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response.status_code == 200


def test_cart_add_item_not_found(fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    response = client.post(f"/add-to-the-cart/{fake.slug()}/", headers=get_headers(shop_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found."}


def test_cart_subtract_success(random_user_data, fake):
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {"quantity": 2}
    response_add = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(shop_id), json=data)
    assert response_add.status_code == 200
    response = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response.status_code == 200


def test_cart_subtract_removed():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    data = {"quantity": 2}
    response_add = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(shop_id), json=data)
    assert response_add.status_code == 200
    response_1 = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response_1.json() == {"detail": "Item removed from the cart."}
    response_2 = client.post(f"/subtract-from-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response_2.json() == {"detail": "Item already removed from the cart."}


def test_cart_get_all_items():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    assert new_shop.status_code == 200
    shop_id = new_shop.json()["id"]
    response = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(shop_id))
    assert response.status_code == 200

    response_cart = client.get(f"/cart/", headers=get_headers(shop_id))
    assert response_cart.status_code == 200
