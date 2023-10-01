from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shop import models, schemas, utils
from shop.smtp_emails import send_status_updated_email
from shop.utils import get_current_shop, get_db

router = APIRouter(prefix="/shop", tags=["shop"])


@router.patch("/", response_model=schemas.ShopOut)
def update_shop_details(
    shop_data: schemas.ShopPatch, current_shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)
):
    shop_data_dict = shop_data.model_dump()

    changed = 0
    for key, value in shop_data_dict.items():
        current_value = getattr(current_shop, key)
        if value is not None:
            if value != current_value:
                if key == "shop_name":
                    utils.check_free_shop_name(db, value)
                    new_slug = utils.generate_unique_shop_slug(db, value)
                    current_shop.slug = new_slug
                    # TODO update all items and categories slugs
                setattr(current_shop, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(current_shop)

    return current_shop


@router.get("/{shop_slug}", response_model=schemas.ShopOut)
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


@router.get("-admin/orders/", response_model=list[schemas.ShopOrderOut])
def get_shop_orders(
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    orders = utils.get_shop_orders(db, current_shop.id)
    return orders


@router.get("-admin/orders/{order_id}", response_model=schemas.ShopOrderOut)
def get_shop_order(
    order_id: int,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    order = utils.get_shop_order_by_order_id(db, order_id, current_shop.id)
    return order


@router.patch("-admin/orders/{order_id}/", response_model=schemas.ShopOrderOut)
def update_shop_order_status(
    order_id: int,
    order_data: schemas.ShopOrderPatch,
    background_tasks: BackgroundTasks,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to update a ShopOrder in the database.

    Parameters:
    - order_data (schemas.ShopOrderPatch): ShopOrder data received from the request body.
    - order_id (int): The id of the ShopOrder to be updated.

    Returns:
    - schemas.ShopOrder: The updated ShopOrder as a Pydantic model.

    Raises:
    - HTTPException 400: If the request data is invalid.
    - HTTPException 404: If the ShopOrder with the given id does not exist.
    """
    order_data_dict = order_data.model_dump()

    order = utils.get_shop_order_by_order_id(db, order_id, current_shop.id)

    changed = 0
    for key, value in order_data_dict.items():
        current_value = getattr(order, key)
        if value is not None:
            if value != current_value:
                setattr(order, key, value)
                background_tasks.add_task(send_status_updated_email, order.user.email, order.status, order.order_id)
                changed = 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(order)

    return order


@router.get("-admin/categories/", response_model=list[schemas.CategoryOut])
def get_all_categories_for_shop_admin(
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all categories for shop admin
    """
    categories = db.query(models.Category).filter(models.Category.shop_id == current_shop.id).all()
    if not categories:
        raise HTTPException(status_code=409, detail="No categories found")
    return categories


@router.get("-admin/items/", response_model=list[schemas.ItemOut])
def get_all_items_for_shop_admin(
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all items for shop admin
    """
    items = db.query(models.Item).filter(models.Item.shop_id == current_shop.id).all()
    if not items:
        raise HTTPException(status_code=409, detail="No items found")
    return items


@router.get("-admin/users/", response_model=list[schemas.UserOut])
def get_all_users_for_shop(
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all users for shop admin
    """
    users = utils.get_all_users_ordered_in_shop(db, current_shop.id)
    return users


@router.get("-admin/users/{user_id}", response_model=list[schemas.ShopOrderOut])
def get_user_orders_shop(
    user_id: int,
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get user for shop admin
    """
    orders = utils.get_shop_orders_by_user_id_for_shop(db, user_id, current_shop.id)
    return orders


@router.get("-admin/stats-items/")
def get_stats_items_per_shop(
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get stats of items per shop
    """
    stats = utils.get_stats_for_each_item(db, current_shop.id)
    return stats


@router.get("-admin/revenue/")
def get_total_revenue_with_filtering(
    start_date: date = Query(None, description="Filter orders by start date"),
    end_date: date = Query(None, description="Filter orders by end date"),
    current_shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get total revenue with filtering by start date and end date
    """
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=409, detail="Start date cannot be greater than end date.")

        revenue = utils.get_total_revenue_with_filtering(db, current_shop.id, str(start_date), str(end_date))
        return revenue
    else:
        revenue = utils.get_total_revenue(db, current_shop.id)
        return revenue
