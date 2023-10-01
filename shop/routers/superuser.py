from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from shop import schemas, utils
from shop.models import User
from shop.utils import get_db

router = APIRouter(prefix="/superuser", tags=["superuser"])


@router.patch("/shop/{shop_slug}/", response_model=schemas.ShopOut)
def update_shop_superuser(
    shop_slug: str,
    shop_data: schemas.ShopPatchAdmin,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    shop_data_dict = shop_data.model_dump()
    shop = utils.get_shop_by_slug(db, shop_slug)
    changed = 0
    for key, value in shop_data_dict.items():
        current_value = getattr(shop, key)
        if value is not None:
            if value != current_value:
                if key == "shop_name":
                    utils.check_free_shop_name(db, value)
                    new_slug = utils.generate_unique_shop_slug(db, value)
                    shop.slug = new_slug
                setattr(shop, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(shop)

    return shop


@router.patch("/item/{item_slug}/", response_model=schemas.ItemOut)
def update_item_superuser(
    item_slug: str,
    item_data: schemas.ItemPatchAdmin,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    item_data_dict = item_data.model_dump()

    item = utils.get_item_by_slug(db, item_slug)
    shop = item.shop
    changed = 0
    for key, value in item_data_dict.items():
        current_value = getattr(item, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    utils.check_free_item_name(db, shop.id, value)
                    setattr(item, "slug", utils.generate_unique_item_slug(db, shop.shop_name, value))
                setattr(item, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(item)

    return item


@router.patch("/category/{category_slug}/", response_model=schemas.CategoryOut)
def update_category_superuser(
    category_slug: str,
    category_data: schemas.CategoryPatch,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    category_data_dict = category_data.model_dump()

    category = utils.get_category_by_slug(db, category_slug)
    shop = category.shop
    changed = 0
    for key, value in category_data_dict.items():
        current_value = getattr(category, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    utils.check_free_category_name(db, shop.id, value)
                    setattr(category, "slug", utils.generate_unique_category_slug(db, shop.shop_name, value))
                setattr(category, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(category)

    return category


@router.patch("/cart-item/{cart_item_id}/", response_model=schemas.CartOut)
def update_cart_item_superuser(
    cart_item_id: int,
    cart_item_data: schemas.PatchCartItemAdmin,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    cart_item_data_dict = cart_item_data.model_dump()

    cart_item = utils.get_cart_item_by_id(db, cart_item_id)
    changed = 0
    for key, value in cart_item_data_dict.items():
        current_value = getattr(cart_item, key)
        if value is not None:
            if value != current_value:
                setattr(cart_item, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.patch("/order/{order_id}/", response_model=schemas.OrderOutAdmin)
def update_order_superuser(
    order_id: int,
    order_data: schemas.OrderPatchAdmin,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    order_data_dict = order_data.model_dump()

    order = utils.get_order_by_order_id(db, order_id)
    changed = 0
    for key, value in order_data_dict.items():
        current_value = getattr(order, key)
        if value is not None:
            if value != current_value:
                setattr(order, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(order)

    return order


@router.patch("/shop-order/{shop_order_id}/", response_model=schemas.ShopOrderOut)
def update_shop_order_superuser(
    shop_order_id: int,
    shop_order_data: schemas.ShopOrderPatchAdmin,
    current_user: User = Depends(utils.get_super_user),
    db: Session = Depends(get_db),
):
    shop_order_data_dict = shop_order_data.model_dump()

    shop_order = utils.get_shop_order_by_id(db, shop_order_id)
    changed = 0
    for key, value in shop_order_data_dict.items():
        current_value = getattr(shop_order, key)
        if value is not None:
            if value != current_value:
                setattr(shop_order, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(shop_order)

    return shop_order


@router.delete("/shop/{shop_slug}/", response_model=schemas.ShopOut)
def delete_shop_superuser(
    shop_slug: str, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    shop = utils.get_shop_by_slug(db, shop_slug)
    user = shop.user
    user.role = "CUSTOMER"
    db.delete(shop)
    db.commit()
    return shop


@router.delete("/item/{item_slug}/", response_model=schemas.ItemOut)
def delete_item_superuser(
    item_slug: str, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    item = utils.get_item_by_slug(db, item_slug)
    db.delete(item)
    db.commit()
    return item


@router.delete("/newsletter/{newsletter_id}/", response_model=schemas.NewsLetterOut)
def delete_newsletter_superuser(
    newsletter_id: int, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    newsletter = utils.get_newsletter_by_id(db, newsletter_id)
    db.delete(newsletter)
    db.commit()
    return newsletter


@router.delete("/item-review/{item_review_id}/", response_model=schemas.ItemReviewOut)
def delete_item_review_superuser(
    item_review_id: int, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    item_review = utils.get_item_review_by_id(db, item_review_id)
    db.delete(item_review)
    db.commit()
    return item_review


@router.delete("/order/{order_id}/", response_model=schemas.OrderOutAdmin)
def delete_order_superuser(
    order_id: int, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    order = utils.get_order_by_order_id(db, order_id)
    # also delete all shop_orders
    shop_orders = order.shop_orders
    for shop_order in shop_orders:
        db.delete(shop_order)

    db.delete(order)
    db.commit()
    return order


@router.delete("/category/{category_slug}/", response_model=schemas.CategoryOut)
def delete_category_superuser(
    category_slug: str, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    category = utils.get_category_by_slug(db, category_slug)
    db.delete(category)
    db.commit()
    return category


@router.delete("/user/{user_id}/", response_model=schemas.UserOut)
def delete_user_superuser(
    user_id: int, current_user: User = Depends(utils.get_super_user), db: Session = Depends(get_db)
):
    user = utils.get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
    return user
