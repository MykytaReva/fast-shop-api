import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from shop import settings
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
            {"sub": str(user_id), "exp": expiration_time}, settings.JWT_SECRET, algorithm=settings.ALGORITHM
        )
        html_content = (
            "You have successfully registered to our shop."
            f" Please click <a href='http://127.0.0.1:8000/verification/?token={token}'>here</a>"
            " to activate your account."
        )
        # Create a Mail object
        message = Mail(
            from_email=os.environ.get("FROM_EMAIL"), to_emails=user_email, subject=subject, html_content=html_content
        )

        # Send the email
        if os.environ.get("ENVIRONMENT") == "test":
            print('You cannot send emails in "test" environment.')
            return {"message": "Email sent successfully."}
        else:
            response = sg.send(message)
            if response.status_code == 202:
                return {"message": "Email sent successfully."}
            else:
                return {"message": "Failed to send email."}
    except Exception as e:
        print("An error occurred:", str(e))
