from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from slugify import slugify
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .auth import authenticate, create_access_token
from .crud import check_free_category_name
from .database import SessionLocal, engine
from .utils import get_current_shop, get_current_user, get_db

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
# TODO add docs field
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
    crud.get_user_by_email_or_username(db, email=user_data.email, username=user_data.username)
    if user_data.role == schemas.UserRoleEnum.SHOP:
        if not user_data.shop_name:
            raise HTTPException(status_code=400, detail="Shop name is required.")
        crud.check_free_shop_name(db, shop_name=user_data.shop_name)

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
    if new_user.role == schemas.UserRoleEnum.SHOP:
        new_user.shop = models.Shop(user_id=new_user.id, shop_name=user_data.shop_name)

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


@app.get("/shop/", response_model=schemas.ShopOut)
def get_shop_details(current_shop: models.Shop = Depends(get_current_shop)):
    """
    Get the shop details of the current logged-in user.
    """
    return current_shop


@app.patch("/shop/", response_model=schemas.ShopOut)
def update_shop_details(
    shop_data: schemas.ShopPatch, current_shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)
):
    allowed_fields = set(schemas.ShopPatch.model_fields.keys())
    shop_data_dict = shop_data.model_dump()
    crud.check_model_fields(shop_data_dict, allowed_fields)

    changed = 0
    for key, value in shop_data_dict.items():
        current_value = getattr(current_shop, key)
        if value is not None:
            if value != current_value:
                if key == "shop_name":
                    crud.check_free_shop_name(db, value)
                setattr(current_shop, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(current_shop)

    return current_shop


@app.post("/category/", response_model=schemas.CategoryOut)
def create_category(
    category_data: schemas.CategoryCreate,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to create a new Category in the database.

    Parameters:
    - category_data (schemas.CategoryCreate): Category data received from the request body.

    Returns:
    - schemas.Category: The newly created Category as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 409: If the slug already exists in the database.
    """
    allowed_fields = set(schemas.CategoryCreate.model_fields.keys())
    category_data_dict = category_data.model_dump()

    crud.check_model_fields(category_data_dict, allowed_fields)
    check_free_category_name(db, current_shop.id, category_data.name)

    category_data.slug = crud.generate_unique_category_slug(db, current_shop.shop_name, category_data.name)

    new_category = models.Category(
        shop_id=current_shop.id,
        name=category_data.name,
        slug=category_data.slug,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@app.delete("/category/{category_slug}/", response_model=schemas.CategoryOut)
def delete_category(
    category_slug: str,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to delete a Category from the database.

    Parameters:
    - category_slug (str): The slug of the Category to be deleted.

    Returns:
    - schemas.Category: The deleted Category as a Pydantic model.

    Raises:
    - HTTPException 404: If the Category with the given slug does not exist.
    """
    category = crud.get_category_by_slug(db, current_shop.id, category_slug)
    db.delete(category)
    db.commit()
    return category


@app.patch("/category/{category_slug}/", response_model=schemas.CategoryOut)
def update_category(
    category_data: schemas.CategoryPatch,
    category_slug: str,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to update a Category in the database.

    Parameters:
    - category_data (schemas.CategoryUpdate): Category data received from the request body.
    - category_slug (str): The slug of the Category to be updated.

    Returns:
    - schemas.Category: The updated Category as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 404: If the Category with the given slug does not exist.
    """
    allowed_fields = set(schemas.CategoryPatch.model_fields.keys())
    category_data_dict = category_data.model_dump()
    crud.check_model_fields(category_data_dict, allowed_fields)

    category = crud.get_category_by_slug(db, current_shop.id, category_slug)

    changed = 0
    for key, value in category_data_dict.items():
        current_value = getattr(category, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    check_free_category_name(db, current_shop.id, value)
                setattr(category, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(category)

    return category


@app.post("/item/", response_model=schemas.ItemOut)
def create_item(
    item_data: schemas.ItemCreate,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to create a new Item in the database.

    Parameters:
    - item_data (schemas.ItemCreate): Item data received from the request body.

    Returns:
    - schemas.Item: The newly created Item as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 409: If the slug already exists in the database.
    """
    allowed_fields = set(schemas.ItemCreate.model_fields.keys())
    item_data_dict = item_data.model_dump()

    crud.check_model_fields(item_data_dict, allowed_fields)
    crud.check_free_item_name(db, current_shop.id, item_data.name)

    item_data.slug = crud.generate_unique_item_slug(db, current_shop.shop_name, item_data.name)

    new_item = models.Item(
        shop_id=current_shop.id,
        category_id=item_data.category_id,
        name=item_data.name,
        slug=item_data.slug,
        image=item_data.image,
        title=item_data.title,
        description=item_data.description,
        price=item_data.price,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item
