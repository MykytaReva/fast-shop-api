from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shop import models, schemas, utils
from shop.utils import get_current_shop, get_current_user, get_db

router = APIRouter(prefix="/item", tags=["items"])


@router.post("/", response_model=schemas.ItemOut)
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
    possible_categories_id = [category.id for category in current_shop.categories]
    if item_data.category_id not in possible_categories_id:
        raise HTTPException(status_code=409, detail="Category not found.")

    utils.check_free_item_name(db, current_shop.id, item_data.name)
    slug = utils.generate_unique_item_slug(db, current_shop.shop_name, item_data.name)

    new_item = models.Item(
        shop_id=current_shop.id,
        category_id=item_data.category_id,
        name=item_data.name,
        slug=slug,
        image=item_data.image,
        title=item_data.title,
        description=item_data.description,
        price=item_data.price,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.patch("/{item_slug}/", response_model=schemas.ItemOut)
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
    item_data_dict = item_data.model_dump()

    item = utils.get_item_by_slug_for_shop(db, current_shop.id, item_slug)
    utils.check_item_owner(db, current_shop.id, item_slug)
    changed = 0
    for key, value in item_data_dict.items():
        current_value = getattr(item, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    utils.check_free_item_name(db, current_shop.id, value)
                    setattr(item, "slug", utils.generate_unique_item_slug(db, current_shop.shop_name, value))
                setattr(item, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(item)

    return item


@router.delete("/{item_slug}/", response_model=schemas.ItemOut)
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


@router.get("/{item_slug}/", response_model=schemas.ItemOut)
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
    # item.reviews for querying the reviews
    item.reviews
    return item


@router.post("/{item_slug}/reviews/", response_model=schemas.ItemReviewOut)
def create_item_comment(
    review_data: schemas.ItemReviewCreate,
    item_slug: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = utils.get_item_by_slug(db, item_slug)
    utils.check_if_user_bought_item(db, current_user.id, item.id)
    if not review_data.stars and not review_data.comment:
        raise HTTPException(status_code=422, detail="You must provide at least one field to create a comment.")
    new_comment = models.ItemReview(
        item_id=item.id,
        user_id=current_user.id,
    )
    if review_data.stars:
        new_comment.stars = review_data.stars

    if review_data.comment:
        new_comment.comment = review_data.comment

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    item._set_average_rating()
    db.commit()
    db.refresh(item)
    return new_comment


@router.get("/{item_slug}/reviews/", response_model=Union[dict, list[schemas.ItemReviewOut]])
def get_item_reviews(
    item_slug: str,
    db: Session = Depends(get_db),
):
    item = utils.get_item_by_slug(db, item_slug)
    reviews = item.reviews
    if not reviews:
        return {"detail": "No reviews found."}
    return reviews
