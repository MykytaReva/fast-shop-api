import secrets

# Generate a random secret key (e.g., 64 characters in length)
JWT_SECRET = secrets.token_urlsafe(64)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
