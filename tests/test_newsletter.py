from unittest.mock import patch

from conftest import client, get_newsletter_and_activate
from jose import jwt

from shop import constants


def test_newsletter_subscribe_success(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response.status_code == 200
    assert response.json() == {
        "email": fake_mail,
        "id": response.json()["id"],
        "is_active": False,
        "created_at": response.json()["created_at"],
    }


def test_newsletter_subscribe_already_exists(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_1 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_1.status_code == 200
    assert response_1.json() == {
        "email": fake_mail,
        "id": response_1.json()["id"],
        "is_active": False,
        "created_at": response_1.json()["created_at"],
    }
    get_newsletter_and_activate(fake_mail)
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_2 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "Email is already signed for newsletter."}


def test_newsletter_subscribe_invalid_email(fake):
    fake_mail = fake.slug()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid email address: The email address is not valid. It must have exactly one @-sign."
    )


def test_newsletter_verify_success(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_1 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_1.status_code == 200
    token = jwt.encode({"sub": fake_mail}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    response_2 = client.get(f"/newsletter/verify/?token={token}")
    assert response_2.status_code == 200
    assert response_2.json() == {"detail": "Email is successfully verified."}


def test_newsletter_verify_already_activated(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_1 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_1.status_code == 200
    get_newsletter_and_activate(fake_mail)
    token = jwt.encode({"sub": fake_mail}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    response_2 = client.get(f"/newsletter/verify/?token={token}")
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "Your email already activated."}


def test_newsletter_unsubscribe_success(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_1 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_1.status_code == 200
    get_newsletter_and_activate(fake_mail)
    token = jwt.encode({"sub": fake_mail}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    response_2 = client.get(f"/newsletter/unsubscribe/?token={token}")
    assert response_2.status_code == 200
    assert response_2.json() == {"detail": "You are successfully unsubscribed."}


def test_newsletter_unsubscribe_already_unsubscribed(fake):
    fake_mail = fake.email()
    with patch("shop.routers.signup.BackgroundTasks.add_task"):
        response_1 = client.post("/newsletter/signup/", json={"email": fake_mail})
    assert response_1.status_code == 200
    token = jwt.encode({"sub": fake_mail}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
    response_2 = client.get(f"/newsletter/unsubscribe/?token={token}")
    assert response_2.status_code == 409
    assert response_2.json() == {"detail": "You are not subscribed for a newsletter."}
