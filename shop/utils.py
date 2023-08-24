import os

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from . import constants
from .auth import oauth2_scheme
from .database import SessionLocal, TestingSessionLocal
from .models import Shop, User
from .schemas import TokenData


# Dependency to get the database session
def get_db():
    if os.getenv("ENVIRONMENT") == "test":
        db = TestingSessionLocal()
        yield db
        db.close()
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            constants.JWT_SECRET,
            algorithms=[constants.ALGORITHM],
            options={"verify_aud": False},
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_shop(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Shop:
    if current_user.role == "SHOP":
        shop = db.query(Shop).filter(Shop.user_id == current_user.id).first()
        return shop
    else:
        raise HTTPException(status_code=403, detail="Forbidden.")
