import os

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from slugify import slugify
from sqlalchemy.orm import Session

from . import constants
from .auth import oauth2_scheme
from .database import SessionLocal, TestingSessionLocal
from .models import CartItem, Category, Item, Shop, User
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
        status_code=401,
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


def check_user_email_or_username(db: Session, email: str, username: str):
    if email:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Email is already taken.")

    if username:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username is already taken.")

    return existing_user


def delete_user_by_id(db: Session, user_id: int):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if existing_user:
        db.delete(existing_user)
        db.commit()
    return existing_user


def get_user_by_id(db: Session, user_id: int):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return existing_user


def get_user_by_email(db: Session, email: str):
    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return existing_user


def check_free_username(db: Session, username: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username is already taken.")

    return existing_user


def get_shop_by_slug(db: Session, shop_slug: str):
    existing_shop = db.query(Shop).filter(Shop.slug == shop_slug).first()
    if not existing_shop:
        raise HTTPException(status_code=404, detail="Shop not found.")
    return existing_shop


def check_free_shop_name(db: Session, shop_name: str):
    if shop_name == "string":
        raise HTTPException(status_code=409, detail="Shop name was not provided.")
    existing_shop = db.query(Shop).filter(Shop.shop_name == shop_name).first()
    if existing_shop:
        raise HTTPException(status_code=409, detail="Shop name is already taken.")

    return existing_shop


def check_model_fields(user_data_dict, allowed_fields):
    allowed_fields.add("additionalProp1")
    for key, value in user_data_dict.items():
        if key not in allowed_fields:
            raise HTTPException(status_code=422, detail=f"Unrecognized field: {key}")


def generate_unique_category_slug(db: Session, shop_name: str, category_name: str):
    unique_slug = f"{slugify(shop_name)}-{slugify(category_name)}"
    counter = 1

    while db.query(Category).filter(Category.slug == unique_slug).first():
        unique_slug = f"{unique_slug}-{counter}"
        counter += 1

    return unique_slug


def generate_unique_shop_slug(db: Session, shop_name: str):
    counter = 1
    unique_slug = shop_name

    while db.query(Shop).filter(Shop.slug == unique_slug).first():
        unique_slug = f"{unique_slug}-{counter}"
        counter += 1

    return unique_slug


def check_free_category_name(db: Session, shop_id: int, category_name: str):
    if category_name == "string":
        raise HTTPException(status_code=409, detail="Category name was not provided.")
    existing_category = db.query(Category).filter(Category.shop_id == shop_id, Category.name == category_name).first()
    if existing_category:
        raise HTTPException(status_code=409, detail=f"You already have category with the name '{category_name}'.")
    return existing_category


def get_category_by_slug(db: Session, shop_id: int, category_slug: str):
    existing_category = db.query(Category).filter(Category.shop_id == shop_id, Category.slug == category_slug).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return existing_category


def generate_unique_item_slug(db: Session, shop_name: str, item_name: str):
    unique_slug = f"{slugify(shop_name)}-{slugify(item_name)}"
    counter = 1

    while db.query(Item).filter(Item.slug == unique_slug).first():
        unique_slug = f"{unique_slug}-{counter}"
        counter += 1

    return unique_slug


def check_free_item_name(db: Session, shop_id: int, item_name: str):
    if item_name == "string":
        raise HTTPException(status_code=409, detail="Item name was not provided.")
    existing_item = db.query(Item).filter(Item.shop_id == shop_id, Item.name == item_name).first()
    if existing_item:
        raise HTTPException(status_code=409, detail=f"You already have item with the name '{item_name}'.")
    return existing_item


# TODO for better understanding consider add one more query to check
#  if category with the given slug exists in general and than check the shop owner
def get_item_by_slug_for_shop(db: Session, shop_id: int, item_slug: str):
    existing_item = db.query(Item).filter(Item.shop_id == shop_id, Item.slug == item_slug).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found.")
    return existing_item


def get_item_by_slug(db: Session, item_slug: str):
    existing_item = db.query(Item).filter(Item.slug == item_slug).first()
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found.")
    return existing_item


def check_item_owner(db: Session, shop_id: int, item_slug: str):
    existing_item = (
        db.query(Item)
        .filter(
            Item.shop_id == shop_id,
            Item.slug == item_slug,
        )
        .first()
    )
    if not existing_item:
        raise HTTPException(status_code=403, detail="Forbidden.")
    return existing_item


def get_cart_item(db: Session, user_id: int, item_id: int):
    existing_cart_item = (
        db.query(CartItem)
        .join(CartItem.item)
        .filter(
            CartItem.user_id == user_id,
            Item.id == item_id,
        )
        .first()
    )
    return existing_cart_item


def get_cart_items(db: Session, user_id: int):
    existing_cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
        )
        .all()
    )
    return existing_cart_items
