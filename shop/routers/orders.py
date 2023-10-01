from collections import defaultdict
from typing import Union

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from shop import constants, models, schemas, utils
from shop.smtp_emails import send_new_order_confirmation_email
from shop.utils import get_current_user, get_db

router = APIRouter(tags=["Related to orders"])

stripe.api_key = constants.STRIPE_API_KEY


@router.get("/cart/")
def get_cart_items(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all CartItems for the current User.
    """
    cart_items = utils.get_cart_items(db, current_user.id)
    total_amount = sum(cart_item.price for cart_item in cart_items)
    cart_out_list = []
    for cart_item in cart_items:
        cart_out = schemas.CartOut(
            item_id=cart_item.item_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
        )
        cart_out_list.append(cart_out)

    cart_out = {"total_amount": total_amount, "cart_items": cart_out_list}

    return cart_out


@router.post("/add-to-the-cart/{item_slug}", response_model=schemas.CartOut)
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


@router.post("/subtract-from-the-cart/{item_slug}/", response_model=Union[schemas.CartOut, dict])
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


@router.get("/order-details/", response_model=list[schemas.CartOut])
def get_order_details(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = utils.get_cart_items(db, current_user.id)
    return cart_items


@router.post("/create-order/", response_model=schemas.OrderOut)
def post_order_details(
    order_data: schemas.OrderBase,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = utils.get_cart_items(db, current_user.id)
    total_paid = sum(cart_item.price for cart_item in cart_items)

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_paid) * 100, currency="usd", metadata={"user_id": current_user.id}
        )
    except stripe.error.StripeError as e:
        # Handle payment error
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)

    except stripe.error.CardError as e:
        # Display error message to the user
        err = e.error
        raise HTTPException(status_code=400, detail=err["message"])

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
        order_key=payment_intent.get("id"),
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    background_tasks.add_task(send_new_order_confirmation_email, current_user.email, new_order)

    for cart_item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id, item_id=cart_item.item_id, quantity=cart_item.quantity, price=cart_item.price
        )

        db.add(order_item)

    shop_items = defaultdict(list)

    for cart_item in cart_items:
        shop_items[cart_item.item.shop_id].append(cart_item)
        db.delete(cart_item)

    for shop_id, cart_items_in_shop in shop_items.items():
        shop_total_price = sum(cart_item.price for cart_item in cart_items_in_shop)
        shop_order = models.ShopOrder(
            shop_id=shop_id, order_id=new_order.id, total_paid=shop_total_price, user_id=current_user.id
        )
        db.add(shop_order)

    db.commit()
    return new_order


@router.post("/stripe-webhook/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    event = None

    try:
        event = stripe.Event.construct_from(payload, stripe.api_key)
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))

    # Handle specific event types
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        order_key = payment_intent.id
        user_id = payment_intent.metadata.user_id

        if user_id is None:
            return {"error": "User ID not found"}
        order = utils.get_order_by_order_key(db, order_key)
        shop_order = db.query(models.ShopOrder).filter(models.ShopOrder.order_id == order.id).first()
        order.billing_status = True
        shop_order.billing_status = True
        db.commit()

    return {"status": "success"}


@router.get("/orders/", response_model=list[schemas.OrderOut])
def get_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = utils.get_orders(db, current_user.id)
    return orders


@router.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = utils.get_order_by_order_id(db, order_id)
    return order


@router.get("/wish-list/")
def get_wish_list_items(
    current_user: models.User = Depends(get_current_user),
):
    """
    Endpoint to get all WishListItems for the current User.
    """
    if not current_user.items:
        return {"detail": "Wish list is empty."}
    return current_user.items


@router.post("/wish-list/{item_slug}")
def add_to_the_wish_list(
    item_slug: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to add an Item to the WishList.
    """
    item = utils.get_item_by_slug(db, item_slug)
    if item:
        if current_user not in item.users:
            current_user.items.append(item)
            db.commit()
            return {"detail": "Item added to the wish list."}
        else:
            current_user.items.remove(item)
            db.commit()
            return {"detail": "Item removed from the wish list."}
