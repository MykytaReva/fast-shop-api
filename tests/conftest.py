import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shop.database import Base
from shop.test_config import DATABASE_URL_TEST


@pytest.fixture
def db():
    engine = create_engine(DATABASE_URL_TEST)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables in the in-memory test database
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    yield db
    db.close()


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

    return {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "email": email,
        "role": "CUSTOMER",
        "is_staff": False,
        "is_active": False,
        "is_superuser": False,
        "password": password,
    }
