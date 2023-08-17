import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()


def send_email_with_sendgrid(subject, to_email, html_content):
    try:
        # Get your SendGrid API key from environment variables
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

        if not sendgrid_api_key:
            raise Exception("SendGrid API key is missing")

        # Create a SendGrid client
        sg = SendGridAPIClient(sendgrid_api_key)

        # Create a Mail object
        message = Mail(
            from_email=os.environ.get("FROM_EMAIL"), to_emails=to_email, subject=subject, html_content=html_content
        )

        # Send the email
        response = sg.send(message)

        if response.status_code == 202:
            return {"message": "Email sent successfully."}
        else:
            return {"message": "Failed to send email."}
    except Exception as e:
        print("An error occurred:", str(e))
