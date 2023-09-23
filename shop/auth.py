from datetime import datetime, timedelta
from typing import List, MutableMapping, Optional, Union

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session

from shop import constants
from shop.models import NewsLetter, User

JWTPayloadMapping = MutableMapping[str, Union[datetime, bool, str, List[str], List[int]]]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def authenticate(*, email: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):  # 1
        return None
    return user


def create_access_token(*, sub: str) -> str:  # 2
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES),  # 3
        sub=sub,
    )


def _create_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    payload = {}
    expire = datetime.utcnow() + lifetime
    payload["type"] = token_type
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    payload["sub"] = str(sub)

    return jwt.encode(payload, constants.JWT_SECRET, constants.ALGORITHM)


def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, constants.JWT_SECRET, algorithms=[constants.ALGORITHM])
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found.")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def verify_token_newsletter(token: str, db: Session):
    try:
        payload = jwt.decode(token, constants.JWT_SECRET, algorithms=[constants.ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Email not found.")

        existing_email = db.query(NewsLetter).filter(NewsLetter.email == email).first()

        if not existing_email:
            raise HTTPException(status_code=404, detail="Email not found.")

        return existing_email

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")

    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token.")
