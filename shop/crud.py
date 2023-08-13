from fastapi import HTTPException
from slugify import slugify
from sqlalchemy.orm import Session

from .models import Category, Shop, User


# TODO consider to refactor it to classes
def get_user_by_email_or_username(db: Session, email: str, username: str):
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


def check_free_username(db: Session, username: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username is already taken.")

    return existing_user


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
