import itertools
from unittest.mock import patch

import factory
from faker import Faker
from fastapi.testclient import TestClient

from shop.auth import create_access_token
from shop.database import TestingSessionLocal
from shop.main import app
from shop.models import Shop, User

client = TestClient(app)
fake = Faker()


def get_shop_and_approve_by_user_id(user_id: int):
    db = TestingSessionLocal()
    shop = db.query(Shop).filter(Shop.user_id == user_id).first()
    if not shop:
        raise ValueError("Shop not found.")
    shop.is_approved = True
    db.commit()
    return shop


def ger_user_by_id_approve(user_id: int):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found.")
    user.is_active = True
    db.commit()
    return user


def delete_user_id(user_id):
    db = TestingSessionLocal()
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


class ShopFactory(factory.Factory):
    class Meta:
        model = dict

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    base_email = factory.Faker("email")
    is_staff = False
    is_active = True
    is_superuser = False
    password = factory.Faker("password")
    shop_name_base = factory.Faker("company")  # Base name for shop_name
    counter = itertools.count(1)  # Counter for appending numbers

    @factory.lazy_attribute
    def shop_name(self):
        return f"{self.shop_name_base}{next(self.counter)}"

    @factory.lazy_attribute
    def email(self):
        return f"{next(self.counter)}{self.base_email}"

    @classmethod
    def _create(cls, model_class, role="SHOP", *args, **kwargs):
        user_data = {
            "username": kwargs["email"],
            "email": kwargs["email"],
            "password": kwargs["password"],
            "role": role,
            "shop_name": kwargs["shop_name"],
            "first_name": kwargs["first_name"],
            "last_name": kwargs["last_name"],
            "is_staff": kwargs["is_staff"],
            "is_active": kwargs["is_active"],
            "is_superuser": kwargs["is_superuser"],
        }

        new_shop = create_user(user_data)
        ger_user_by_id_approve(new_shop.json()["id"])
        if new_shop.status_code != 200:
            raise ValueError(new_shop.json())
        assert new_shop.status_code == 200
        if role == "SHOP":
            get_shop_and_approve_by_user_id(new_shop.json()["id"])
            category_data = {"name": "fixture-category"}
            response_category = client.post("category/", headers=get_headers(new_shop.json()["id"]), json=category_data)
            assert response_category.status_code == 200
            category_id = response_category.json()["id"]
            category_slug = response_category.json()["slug"]
            category_name = response_category.json()["name"]
            item_data = {
                "name": "fixture-item",
                "description": "fixture-description",
                "title": "fixture-title",
                "image": "/fixtureimage.jpg",
                "price": 10.0,
                "category_id": category_id,
            }
            response_item = client.post("/item/", headers=get_headers(new_shop.json()["id"]), json=item_data)
            assert response_item.status_code == 200
            item_slug = response_item.json()["slug"]
            item_id = response_item.json()["id"]
            cart_response = client.post(f"/add-to-the-cart/{item_slug}/", headers=get_headers(new_shop.json()["id"]))
            return {
                "new_shop": new_shop,
                "category_id": category_id,
                "category_name": category_name,
                "category_slug": category_slug,
                "item_id": item_id,
                "item_slug": item_slug,
                "cart_response": cart_response,
            }
        else:
            return {"new_user": new_shop}
