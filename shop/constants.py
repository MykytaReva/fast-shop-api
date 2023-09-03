import os
import secrets

from dotenv import load_dotenv

load_dotenv()
# Generate a random secret key (e.g., 64 characters in length)
JWT_SECRET = secrets.token_urlsafe(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

STRIPE_API_KEY = os.environ.get("STRIPE_SECRET_KEY")

HOST = os.environ.get("HOST")

FROM_EMAIL = os.environ.get("FROM_EMAIL")
