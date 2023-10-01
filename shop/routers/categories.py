from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shop import models, schemas, utils
from shop.utils import get_current_shop, get_db

router = APIRouter(prefix="/category", tags=["categories"])


@router.post("/", response_model=schemas.CategoryOut)
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
    utils.check_free_category_name(db, current_shop.id, category_data.name)

    slug = utils.generate_unique_category_slug(db, current_shop.shop_name, category_data.name)

    new_category = models.Category(
        shop_id=current_shop.id,
        name=category_data.name,
        slug=slug,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.delete("/{category_slug}/", response_model=schemas.CategoryOut)
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
    category = utils.get_category_by_slug_and_shop_id(db, current_shop.id, category_slug)
    db.delete(category)
    db.commit()
    return category


@router.patch("/{category_slug}/", response_model=schemas.CategoryOut)
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
    category_data_dict = category_data.model_dump()

    category = utils.get_category_by_slug_and_shop_id(db, current_shop.id, category_slug)

    changed = 0
    for key, value in category_data_dict.items():
        current_value = getattr(category, key)
        if value is not None:
            if value != current_value:
                if key == "name":
                    utils.check_free_category_name(db, current_shop.id, value)
                    setattr(category, "slug", utils.generate_unique_category_slug(db, current_shop.shop_name, value))
                setattr(category, key, value)
                changed += 1
    if not changed:
        raise HTTPException(status_code=422, detail="Model was not changed.")

    db.commit()
    db.refresh(category)

    return category
