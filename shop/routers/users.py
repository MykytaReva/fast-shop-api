from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shop import models, schemas, utils
from shop.utils import get_current_user, get_db

router = APIRouter(prefix="/user", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Fetch the current logged-in user.
    """

    user = current_user
    return user


# TODO add notification that not possible to patch email
@router.patch("/", response_model=schemas.UserProfileOut)
def update_user_details(
    user_data: schemas.UserCompletePatch,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the details of a user by their unique 'user_id'.
    Allows partial updates by providing only the fields that need to be changed in the request payload.
    """
    # tests fields provided
    user_data_dict = user_data.model_dump()

    # separate fields for models
    allowed_fields_user = set(schemas.UserPatch.model_fields.keys())
    allowed_fields_profile = set(schemas.UserProfilePatch.model_fields.keys())

    profile = current_user.profile

    # variable to tests if model has been changed
    changed = 0

    # assign new values if changed
    for key, value in user_data_dict.items():
        if key in allowed_fields_user:
            current_value = getattr(current_user, key)
            if value is not None:
                if key == "password":
                    current_user.set_password(value)
                    continue
                if value != current_value:
                    if key == "username":
                        utils.check_free_username(db, value)
                    setattr(current_user, key, value)
                    changed += 1
        elif key in allowed_fields_profile:
            current_value = getattr(profile, key)
            if value is not None:
                if value != current_value:
                    setattr(profile, key, value)
                    changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/")
def delete_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    utils.delete_user_by_id(db, current_user.id)
    return {"message": "User deleted successfully."}


@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
