from collections import defaultdict
from typing import Union

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, utils
from .auth import authenticate, create_access_token, verify_token
from .database import SessionLocal, engine
from .smtp_emails import send_activation_email, send_reset_password_email
from .utils import check_free_category_name, get_current_shop, get_current_user, get_db

app = FastAPI()

# Create all tables in the database (if they don't exist)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    # for fun
    content = """
    <h1>Sign Up</h1>
    <form action="/signup/" method="post">
        <!-- User Data -->
        <label for="first_name">First Name:</label>
        <input type="text" name="first_name"><br>

        <label for="last_name">Last Name:</label>
        <input type="text" name="last_name"><br>

        <label for="username">Username:</label>
        <input type="text" name="username"><br>

        <label for="email">Email:</label>
        <input type="email" name="email"><br>

        <label for="password">Password:</label>
        <input type="password" name="password"><br>

        <label for="role">Role:</label>
        <select name="role">
            <option value="USER">User</option>
            <option value="SHOP">Shop</option>
        </select><br>

        <!-- Shop Name (if role is SHOP) -->
        <label for="shop_name">Shop Name:</label>
        <input type="text" name="shop_name"><br>

        <input type="submit" value="Sign Up">
    </form>
        """
    return HTMLResponse(content=content)


@app.get("/users/", response_model=list[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """
    Endpoint to get all users
    """
    users = db.query(models.User).all()
    return users


@app.post("/signup/", response_model=schemas.UserOut)
async def signup(user_data: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
    utils.check_model_fields(user_data_dict, allowed_fields)

    # tests if user exists and handle unique constraints error
    utils.check_user_email_or_username(db, email=user_data.email, username=user_data.username)
    if user_data.role == schemas.UserRoleEnum.SHOP:
        if not user_data.shop_name:
            raise HTTPException(status_code=400, detail="Shop name is required.")
        utils.check_free_shop_name(db, shop_name=user_data.shop_name)

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
        slug = utils.generate_unique_shop_slug(db, user_data.shop_name)
        new_user.shop = models.Shop(user_id=new_user.id, shop_name=user_data.shop_name, slug=slug)
        # new_user.shop = models.Shop(user_id=new_user.id, shop_name=user_data.shop_name)

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    background_tasks.add_task(send_activation_email, new_user.id, db)

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


# TODO consider make response_model with a userprofile fields in future
@app.get("/user/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@app.delete("/user/")
def delete_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    utils.delete_user_by_id(db, current_user.id)
    return {"message": "User deleted successfully."}


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
    utils.check_model_fields(user_data_dict, allowed_fields)

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


@app.get("/shop/{shop_slug}", response_model=schemas.ShopOut)
def get_shop(shop_slug: str, db: Session = Depends(get_db)):
    """
    Endpoint to get a Shop from the database.

    Parameters:
    - shop_slug (str): The slug of the Shop to be fetched.

    Returns:
    - schemas.Shop: The fetched Shop as a Pydantic model.

    Raises:
    - HTTPException 404: If the Shop with the given slug does not exist.
    """
    shop = utils.get_shop_by_slug(db, shop_slug)
    return shop


@app.patch("/shop/", response_model=schemas.ShopOut)
def update_shop_details(
    shop_data: schemas.ShopPatch, current_shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)
):
    allowed_fields = set(schemas.ShopPatch.model_fields.keys())
    shop_data_dict = shop_data.model_dump()
    utils.check_model_fields(shop_data_dict, allowed_fields)

    changed = 0
    for key, value in shop_data_dict.items():
        current_value = getattr(current_shop, key)
        if value is not None:
            if value != current_value:
                if key == "shop_name":
                    utils.check_free_shop_name(db, value)
                    new_slug = utils.generate_unique_shop_slug(db, value)
                    current_shop.slug = new_slug
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

    utils.check_model_fields(category_data_dict, allowed_fields)
    check_free_category_name(db, current_shop.id, category_data.name)

    category_data.slug = utils.generate_unique_category_slug(db, current_shop.shop_name, category_data.name)

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
    category = utils.get_category_by_slug(db, current_shop.id, category_slug)
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
    utils.check_model_fields(category_data_dict, allowed_fields)

    category = utils.get_category_by_slug(db, current_shop.id, category_slug)

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

    utils.check_model_fields(item_data_dict, allowed_fields)
    utils.check_free_item_name(db, current_shop.id, item_data.name)

    item_data.slug = utils.generate_unique_item_slug(db, current_shop.shop_name, item_data.name)

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


@app.patch("/item/{item_slug}/", response_model=schemas.ItemOut)
def update_item(
    item_data: schemas.ItemPatch,
    item_slug: str,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to update an Item in the database.

    Parameters:
    - item_data (schemas.ItemUpdate): Item data received from the request body.
    - item_slug (str): The slug of the Item to be updated.

    Returns:
    - schemas.Item: The updated Item as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 404: If the Item with the given slug does not exist.
    """
    allowed_fields = set(schemas.ItemPatch.model_fields.keys())
    item_data_dict = item_data.model_dump()
    utils.check_model_fields(item_data_dict, allowed_fields)

    item = utils.get_item_by_slug_for_shop(db, current_shop.id, item_slug)
    utils.check_item_owner(db, current_shop.id, item_slug)
    changed = 0
    for key, value in item_data_dict.items():
        current_value = getattr(item, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    utils.check_free_item_name(db, current_shop.id, value)
                setattr(item, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(item)

    return item


@app.delete("/item/{item_slug}/", response_model=schemas.ItemOut)
def delete_item(
    item_slug: str,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to delete an Item from the database.

    Parameters:
    - item_slug (str): The slug of the Item to be deleted.

    Returns:
    - schemas.Item: The deleted Item as a Pydantic model.

    Raises:
    - HTTPException 404: If the Item with the given slug does not exist.
    """
    item = utils.get_item_by_slug_for_shop(db, current_shop.id, item_slug)
    # utils.check_item_owner(db, current_shop.id, item_slug)
    db.delete(item)
    db.commit()
    return item


@app.get("/item/{item_slug}/", response_model=schemas.ItemOut)
def get_item(
    item_slug: str,
    db: Session = Depends(get_db),
):
    """
    Endpoint to get an Item from the database.

    Parameters:
    - item_slug (str): The slug of the Item to be fetched.

    Returns:
    - schemas.Item: The fetched Item as a Pydantic model.

    Raises:
    - HTTPException 404: If the Item with the given slug does not exist.
    """
    item = utils.get_item_by_slug(db, item_slug)
    return item


# TODO HTMLResponse?
@app.get("/verification/", response_class=HTMLResponse)
async def email_verification(request: Request, token: str, db: Session = Depends(get_db)):
    """
    Endpoint to verify user's email.
    """
    user = verify_token(token, db)
    if user and not user.is_active:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return HTMLResponse(content="<h1>Email verified</h1>", status_code=200)
    else:
        return HTMLResponse(content="<h1>Your account already activated.</h1>", status_code=400)


@app.get("/reset-password/")
async def request_password_reset():
    """
    Endpoint to request password reset.
    """
    return {"message": "Please provide email address"}


@app.post("/reset-password/")
async def request_password_reset(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint to request email for password reset.
    """
    user = utils.get_user_by_email(db, email=email)
    if user:
        background_tasks.add_task(send_reset_password_email, user_id=user.id, email=email, db=db)
        return {"message": f"Link to reset password has been sent to {email}"}


@app.get("/reset-password/verify/")
async def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """
    Endpoint to verify reset password token.
    """
    user = verify_token(token, db)
    if user:
        return {"message": "Please provide new password."}


@app.post("/reset-password/verify/")
async def reset_password(token: str, request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to change password.
    """
    data = await request.json()
    new_password = data.get("new_password")
    user = verify_token(token, db)
    if user:
        user.set_password(new_password)
        db.commit()
        db.refresh(user)
        return {"detail": "Password has been changed."}


@app.post("/add-to-the-cart/{item_slug}", response_model=schemas.CartOut)
def add_to_the_cart(
    item_slug: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to add an Item to the Cart.
    """
    item = utils.get_item_by_slug(db, item_slug)
    if item:
        cart_item = utils.get_cart_item(db, current_user.id, item.id)
        if cart_item:
            cart_item.quantity += 1
            cart_item.price = item.price * cart_item.quantity
            db.commit()
            db.refresh(cart_item)
            return cart_item
        else:
            cart_item = models.CartItem(user_id=current_user.id, item_id=item.id, price=item.price)
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item


@app.get("/cart/", response_model=list[schemas.CartOut])
def get_cart_items(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all CartItems for the current User.
    """
    cart_items = utils.get_cart_items(db, current_user.id)
    return cart_items


@app.post("/subtract-from-the-cart/{item_slug}/", response_model=Union[schemas.CartOut, dict])
def subtract_from_the_cart(
    item_slug: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to subtract an Item from the Cart.
    """
    item = utils.get_item_by_slug(db, item_slug)
    if item:
        cart_item = utils.get_cart_item(db, current_user.id, item.id)
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.price = item.price * cart_item.quantity
                db.commit()
                db.refresh(cart_item)
                return cart_item
            else:
                db.delete(cart_item)
                db.commit()
                return {"detail": "Item removed from the cart."}
        else:
            return {"detail": "Item already removed from the cart."}


@app.get("/order-details/", response_model=list[schemas.CartOut])
def get_order_details(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = crud.get_cart_items(db, current_user.id)
    return cart_items


@app.post("/create-order/", response_model=schemas.OrderOut)
def post_order_details(
    order_data: schemas.OrderBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    cart_items = crud.get_cart_items(db, current_user.id)
    total_paid = sum(cart_item.price for cart_item in cart_items)

    new_order = models.Order(
        first_name=order_data.first_name,
        last_name=order_data.last_name,
        user_id=current_user.id,
        total_paid=total_paid,
        address=order_data.address,
        city=order_data.city,
        country=order_data.country,
        pin_code=order_data.pin_code,
        phone_number=order_data.phone_number,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart_items:
        order_item = models.OrderItem(order_id=new_order.id, item_id=item.id, quantity=item.quantity, price=item.price)
        db.add(order_item)

    shop_items = defaultdict(list)

    for cart_item in cart_items:
        shop_items[cart_item.item.shop_id].append(cart_item)
        db.delete(cart_item)

    for shop_id, cart_items_in_shop in shop_items.items():
        shop_total_price = sum(cart_item.price for cart_item in cart_items_in_shop)
        shop_order = models.ShopOrder(shop_id=shop_id, order_id=new_order.id, total_paid=shop_total_price)
        db.add(shop_order)

    db.commit()
    return new_order
