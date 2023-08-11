from . import settings
from .auth import oauth2_scheme
from .database import SessionLocal
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from .models import User
from .schemas import TokenData
from .test_config import SQLALCHEMY_DATABASE_URL


# Dependency to get the database session
def get_db():
    if os.getenv("ENVIRONMENT") == "test":
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create tables in the in-memory test database
        Base.metadata.create_all(bind=engine)

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
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
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


# function which will get the current user and check if this user has shop,
# if user has shop we need to return a shop object
def get_current_shop(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Shop:
    if current_user.role == "SHOP":
        shop = db.query(Shop).filter(Shop.user_id == current_user.id).first()
        return shop
    else:
        raise HTTPException(status_code=404, detail="User is not a shop.")
