from fastapi import HTTPException
from .models import User
from sqlalchemy.orm import Session


# TODO consider to refactor it to classes
def get_user_by_email_or_username(db: Session, email: str, username: str, user_data):
    if email:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Email is already taken.")

    if username:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username is already taken.")

    return existing_user


# Session.query(User).filter(User.email == 'asdfasdf').first()


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


def check_model_fields(user_data_dict, allowed_fields):
    allowed_fields.add("additionalProp1")
    for key, value in user_data_dict.items():
        if key not in allowed_fields:
            raise HTTPException(status_code=422, detail=f"Unrecognized field: {key}")
