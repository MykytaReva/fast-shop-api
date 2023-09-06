from tests.conftest import (
    client,
    delete_user,
    get_amount_of_all_items,
    get_amount_of_items_per_shop,
    get_headers,
    get_shop_by_user_id,
)
from tests.factories import ShopFactory


def test_add_remove_to_wishlist_success():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    user_id = new_shop.json()["id"]
    response_add = client.post(f"/wish-list/{item_slug}", headers=get_headers(user_id), json={"item_slug": item_slug})
    assert response_add.status_code == 200
    assert response_add.json() == {"detail": "Item added to the wish list."}

    response_remove = client.post(
        f"/wish-list/{item_slug}", headers=get_headers(user_id), json={"item_slug": item_slug}
    )
    assert response_remove.status_code == 200
    assert response_remove.json() == {"detail": "Item removed from the wish list."}


def test_get_wishlist_items():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    item_slug = user_data_dict["item_slug"]
    user_id = new_shop.json()["id"]
    response_add = client.post(f"/wish-list/{item_slug}", headers=get_headers(user_id), json={"item_slug": item_slug})
    assert response_add.status_code == 200
    assert response_add.json() == {"detail": "Item added to the wish list."}

    response_get = client.get(f"/wish-list/", headers=get_headers(user_id))
    assert response_get.status_code == 200
    assert response_get.json()[0]["name"] == "fixture-item"


def test_get_wishlist_empty():
    user_data_dict = ShopFactory.create()
    new_shop = user_data_dict["new_shop"]
    user_id = new_shop.json()["id"]
    response_get = client.get(f"/wish-list/", headers=get_headers(user_id))
    assert response_get.status_code == 200
    assert response_get.json() == {"detail": "Wish list is empty."}
