from unittest.mock import patch

import pytest
from faker import Faker
from fastapi import HTTPException
from fastapi.testclient import TestClient

from shop.auth import create_access_token
from shop.database import TestingSessionLocal
from shop.main import app
from shop.models import Shop, ShopOrder, User

client = TestClient(app)


def create_order(data, shop_id: int):
    mock_payment_intent = {"id": "mocked_payment_intent_id"}
    with patch("shop.main.stripe.PaymentIntent.create", return_value=mock_payment_intent):
        response = client.post(f"/create-order/", headers=get_headers(shop_id), json=data)
    return response


def get_shop_order_by_order_id(shop_id: int, order_id: int):
    db = TestingSessionLocal()
    shop_order = db.query(ShopOrder).filter(ShopOrder.shop_id == shop_id, ShopOrder.order_id == order_id).first()
    if not shop_order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return shop_order


def get_shop_by_shop_id(shop_id: int):
    db = TestingSessionLocal()
    shop = db.query(Shop).filter(Shop.user_id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found.")
    return shop


def delete_user(response_json):
    db = TestingSessionLocal()
    user_id = response_json.json().get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def create_user(data):
    with patch("shop.main.BackgroundTasks.add_task"):
        response = client.post("/signup/", json=data)
    return response


def get_headers(user_id: int):
    token = create_access_token(sub=str(user_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def random_user_data(fake):
    username = fake.user_name()
    email = fake.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password()
    shop_name = fake.company()

    return {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "role": "CUSTOMER",
        "shop_name": shop_name,
        "is_staff": False,
        "is_active": False,
        "is_superuser": False,
        "password": password,
    }


@pytest.fixture
def random_second_user(fake):
    username = fake.user_name()
    email = fake.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    password = fake.password()
    shop_name = fake.company()

    return {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "role": "CUSTOMER",
        "shop_name": shop_name,
        "is_staff": False,
        "is_active": False,
        "is_superuser": False,
        "password": password,
    }


# @pytest.fixture
# def new_shop(random_user_data):
#     random_user_data["role"] = "SHOP"
#     user = create_user(random_user_data)
#     yield user


@pytest.fixture
def new_user(random_user_data):
    user = create_user(random_user_data)
    yield user


@pytest.fixture
def new_shop_with_category_and_item(new_shop):
    data_category = {
        "name": "fixture-category",
    }
    shop_id = new_shop.json()["id"]
    response_category = client.post("/category/", headers=get_headers(shop_id), json=data_category)
    assert response_category.status_code == 200
    category_slug = response_category.json()["slug"]
    category_id = response_category.json()["id"]
    data_item = {
        "name": "fixture-item",
        "image": "https://picsum.photos/200/300",
        "title": "fixture-title",
        "description": "fixture-description",
        "price": 100,
        "category_id": category_id,
    }
    response_item = client.post("/item/", headers=get_headers(shop_id), json=data_item)
    assert response_item.status_code == 200
    item_id = response_item.json()["id"]
    item_slug = response_item.json()["slug"]
    return {
        "new_shop": new_shop,
        "category_id": category_id,
        "category_slug": category_slug,
        "item_id": item_id,
        "item_slug": item_slug,
    }


@pytest.fixture
def random_user_data_shop(fake):
    shop_name = fake.company()
    description = fake.text()

    return {"shop_name": shop_name, "description": description}


@pytest.fixture
def random_item_data(fake):
    name = fake.name()
    image = fake.image_url()
    title = fake.text()
    description = fake.text()
    price = fake.pyint()

    return {
        "name": name,
        "image": image,
        "title": title,
        "description": description,
        "price": price,
    }


@pytest.fixture
def order_data():
    return {
        "first_name": "string",
        "last_name": "string",
        "phone_number": "string",
        "address": "string",
        "country": "string",
        "city": "string",
        "pin_code": "string",
    }
