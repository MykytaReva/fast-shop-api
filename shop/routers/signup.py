from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shop import models, schemas, utils
from shop.auth import authenticate, create_access_token, verify_token, verify_token_newsletter
from shop.smtp_emails import send_activation_email, send_newsletter_activation_email, send_reset_password_email

router = APIRouter(tags=["Signup"])


@router.post("/signup/", response_model=schemas.UserOut)
async def signup(user_data: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(utils.get_db)):
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


@router.post("/login")
def login(db: Session = Depends(utils.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get the JWT for a user with data from OAuth2 request form body.
    """
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        # TODO show what exactly is incorrect
        raise HTTPException(status_code=400, detail="Incorrect credentials.")
    return {"access_token": create_access_token(sub=user.id), "token_type": "bearer"}


@router.get("/verification/")
async def email_verification(request: Request, token: str, db: Session = Depends(utils.get_db)):
    """
    Endpoint to verify user's email.
    """
    user = verify_token(token, db)
    if user and not user.is_active:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return {"detail": "Your account successfully activated."}
    else:
        return {"detail": "Your account already activated."}


@router.get("/reset-password/")
async def request_password_reset():
    """
    Endpoint to request password reset.
    """
    return {"message": "Please provide email address"}


@router.post("/reset-password/")
async def request_password_reset(email: str, background_tasks: BackgroundTasks, db: Session = Depends(utils.get_db)):
    """
    Endpoint to request email for password reset.
    """
    user = utils.get_user_by_email(db, email=email)
    if user:
        background_tasks.add_task(send_reset_password_email, user_id=user.id, email=email, db=db)
        return {"message": f"Link to reset password has been sent to {email}"}


@router.get("/reset-password/verify/")
async def verify_reset_token(token: str, db: Session = Depends(utils.get_db)):
    """
    Endpoint to verify reset password token.
    """
    user = verify_token(token, db)
    if user:
        return {"message": "Please provide new password."}


@router.post("/reset-password/verify/")
async def reset_password(token: str, request: Request, db: Session = Depends(utils.get_db)):
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


@router.post("/newsletter/signup/", response_model=schemas.NewsLetterOut)
async def newsletter_signup(
    newsletter_data: schemas.NewsLetterBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(utils.get_db),
):
    """
    Endpoint to create a new Newsletter in the database.

    Parameters:
    - newsletter_data (schemas.NewsletterCreate): Newsletter data received from the request body.

    Returns:
    - schemas.Newsletter: The newly created Newsletter as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 409: If the slug already exists in the database.
    """
    utils.check_if_email_already_signed_for_newsletter(db, newsletter_data.email)
    newsletter = db.query(models.NewsLetter).filter(models.NewsLetter.email == newsletter_data.email).first()
    if not newsletter:
        newsletter = models.NewsLetter(
            email=newsletter_data.email,
        )
        db.add(newsletter)
        db.commit()
        db.refresh(newsletter)
    background_tasks.add_task(send_newsletter_activation_email, newsletter_data.email)

    return newsletter


@router.get("/newsletter/verify/")
async def email_verification_newsletter(token: str, db: Session = Depends(utils.get_db)):
    """
    Endpoint to verify user's email for newsletter.
    """
    newsletter = verify_token_newsletter(token, db)
    if newsletter and not newsletter.is_active:
        newsletter.is_active = True
        db.commit()
        db.refresh(newsletter)
        return {"detail": "Email is successfully verified."}
    else:
        raise HTTPException(status_code=409, detail="Your email already activated.")


@router.get("/newsletter/unsubscribe/")
async def email_unsubscribe_newsletter(token: str, db: Session = Depends(utils.get_db)):
    """
    Endpoint to unsubscribe user's email from newsletter.
    """
    newsletter = verify_token_newsletter(token, db)
    if newsletter and newsletter.is_active:
        newsletter.is_active = False
        db.commit()
        db.refresh(newsletter)
        return {"detail": "You are successfully unsubscribed."}
    else:
        raise HTTPException(status_code=409, detail="You are not subscribed for a newsletter.")
