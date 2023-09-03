import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from shop import constants
from shop.database import SessionLocal
from shop.models import User

load_dotenv()


def send_activation_email(user_id: int, db: SessionLocal):
    try:
        # Get your SendGrid API key from environment variables
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

        if not sendgrid_api_key:
            raise Exception("SendGrid API key is missing")

        # Create a SendGrid client
        sg = SendGridAPIClient(sendgrid_api_key)

        user_email = db.query(User).filter(User.id == user_id).first().email
        subject = "Welcome to our shop!"
        expiration_time = datetime.utcnow() + timedelta(minutes=5)
        token = jwt.encode(
            {"sub": str(user_id), "exp": expiration_time}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
        )
        html_content = (
            "You have successfully registered to our shop."
            f" Please click <a href='http://{constants.HOST}/verification/?token={token}'>here</a>"
            " to activate your account."
        )
        # Create a Mail object
        message = Mail(
            from_email=constants.FROM_EMAIL, to_emails=user_email, subject=subject, html_content=html_content
        )

        # Send the email
        print('Email sent in "development" environment.')
        sg.send(message)
    except Exception as e:
        print("An error occurred:", str(e))


def send_reset_password_email(user_id: int, email: str, db: SessionLocal):
    try:
        # Get your SendGrid API key from environment variables
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

        if not sendgrid_api_key:
            raise Exception("SendGrid API key is missing")

        # Create a SendGrid client
        sg = SendGridAPIClient(sendgrid_api_key)

        subject = "Reset Your Password"
        expiration_time = datetime.utcnow() + timedelta(hours=12)
        reset_token = jwt.encode(
            {"sub": str(user_id), "exp": expiration_time}, constants.JWT_SECRET, algorithm=constants.ALGORITHM
        )
        html_content = (
            f"Click <a href='http://{constants.HOST}/reset-password/verify/?token={reset_token}'>here</a>"
            " to reset your password."
        )
        # Create a Mail object
        message = Mail(
            from_email=os.environ.get("FROM_EMAIL"), to_emails=email, subject=subject, html_content=html_content
        )

        # Send the email
        print('Email sent in "development" environment.')
        sg.send(message)

    except Exception as e:
        print("An error occurred:", str(e))


def send_newsletter_activation_email(email: str):
    try:
        # Get your SendGrid API key from environment variables
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

        if not sendgrid_api_key:
            raise Exception("SendGrid API key is missing")

        # Create a SendGrid client
        sg = SendGridAPIClient(sendgrid_api_key)

        subject = "Activate Your Subscription"
        expiration_time = datetime.utcnow() + timedelta(hours=12)
        token = jwt.encode({"sub": email, "exp": expiration_time}, constants.JWT_SECRET, algorithm=constants.ALGORITHM)
        html_content = (
            f"Click <a href=http://{constants.HOST}/newsletter/verify/?token={token}>here</a>"
            " to activate your subscription."
        )

        # Create a Mail object
        message = Mail(
            from_email=os.environ.get("FROM_EMAIL"), to_emails=email, subject=subject, html_content=html_content
        )

        # Send the email
        print('Email sent in "development" environment.')
        sg.send(message)

    except Exception as e:
        print("An error occurred:", str(e))
