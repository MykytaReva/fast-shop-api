import os
import secrets

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.environ.get("ENV")
# Generate a random secret key (e.g., 64 characters in length)
JWT_SECRET = secrets.token_urlsafe(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

STRIPE_API_KEY = os.environ.get("STRIPE_SECRET_KEY")

HOST = os.environ.get("HOST")
FROM_EMAIL = os.environ.get("FROM_EMAIL")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
