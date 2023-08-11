from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .auth import authenticate, create_access_token
from .database import SessionLocal, engine
from .utils import get_current_user, get_db

app = FastAPI()

# Create all tables in the database (if they don't exist)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/", response_model=list[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """
    Endpoint to get all users
    """
    users = db.query(models.User).all()
    return users


# TODO rename to sign_up and change url
@app.post("/signup/", response_model=schemas.UserOut)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new user in the database.

    Parameters:
    - user_data (schemas.UserCreate): User data received from the request body, including the password.

    Returns:
    - schemas.User: The newly created user as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 409: If the email or username already exists in the database.
    """
    # tests fields provided
    allowed_fields = set(schemas.UserCreate.model_fields.keys())
    user_data_dict = user_data.model_dump()
    crud.check_model_fields(user_data_dict, allowed_fields)

    # tests if user exists and handle unique constraints error
    crud.get_user_by_email_or_username(db, email=user_data.email, username=user_data.username, user_data=user_data)

    # Create a new User object using UserCreate schema
    new_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        email=user_data.email,
        role=user_data.role.value,
    )
    # Hash the password before saving to the database
    new_user.set_password(user_data.password)
    new_user.profile = models.UserProfile()

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    # Return the newly created user as a Pydantic model
    return new_user


@app.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get the JWT for a user with data from OAuth2 request form body.
    """
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        # TODO show what exactly is incorrect
        raise HTTPException(status_code=400, detail="Incorrect credentials.")
    return {"access_token": create_access_token(sub=user.id), "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Fetch the current logged-in user.
    """

    user = current_user
    return user


# TODO consider make it with a userprofile fields
@app.get("/user/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@app.delete("/user/")
def delete_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    crud.delete_user_by_id(db, current_user.id)
    return {"message": "User deleted successfully."}


# TODO returns profile fields as a null in UserProfileOut response model
# TODO add notification that not possible to patch email
@app.patch("/user/", response_model=schemas.UserProfileOut)
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
    allowed_fields = set(schemas.UserCompletePatch.model_fields.keys())
    user_data_dict = user_data.model_dump()
    crud.check_model_fields(user_data_dict, allowed_fields)

    # separate fields for models
    allowed_fields_user = set(schemas.UserPatch.model_fields.keys())
    allowed_fields_profile = set(schemas.UserProfilePatch.model_fields.keys())

    # get user and profile

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
                        crud.check_free_username(db, value)
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
