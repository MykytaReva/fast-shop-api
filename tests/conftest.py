import pytest
from faker import Faker

from tests.test_user_crud import client, create_user, get_headers


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


# @pytest.fixture
# def new_shop_user_id(random_user_data):
#     # random_user_data["role"] = "SHOP"
#     # user = create_user(random_user_data)
#     # assert user.status_code == 200
#     # return user.json()["id"]
#     return 5
#
#
# @pytest.fixture
# def new_category_id(new_shop_user_id, fake):
#     category_data = {
#         "name": f"{fake.company()}-category"
#     }
#     response_category = client.post("category/", headers=get_headers(new_shop_user_id), json=category_data)
#     assert response_category.status_code == 200
#     return response_category.json()["id"]
