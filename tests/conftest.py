import pytest
from faker import Faker


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
