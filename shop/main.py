from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from shop import constants, models, schemas
from shop.database import engine
from shop.routers import categories, items, orders, shops, signup, users
from shop.utils import get_db

if constants.ENVIRONMENT == "prod":
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()

app.include_router(users.router)
app.include_router(signup.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(shops.router)
app.include_router(orders.router)


# Create all tables in the database (if they don't exist)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    # for fun
    content = """
    <h1>Welcome to shop-online API.</h1>
    <h2>Documentation:</h2>
    <ul>
        <li><a href="/docs">Swagger UI</a></li>
        <li><a href="/redoc">ReDoc</a></li>
    </ul>
        """
    return HTMLResponse(content=content)


@app.get("/users/", response_model=list[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """
    Endpoint to get all users
    """
    users = db.query(models.User).all()
    return users


@app.get("/items/", response_model=list[schemas.ItemOut])
def get_all_items_with_filtering(
    shop: str = Query(None, description="Filter items by shop slug"),
    category: str = Query(None, description="Filter items by category name"),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get all items with filtering by shop's name and category's name
    """
    all_items = (
        db.query(models.Item)
        .filter(
            models.Item.is_approved == True,
            models.Item.is_available == True,
        )
        .all()
    )
    if shop:
        shop_exists = db.query(models.Shop).filter(models.Shop.slug == shop).first()
        if shop_exists:
            items_by_shop = (
                db.query(models.Item)
                .join(models.Item.shop)
                .filter(
                    models.Shop.slug == shop,
                    models.Item.is_approved == True,
                    models.Item.is_available == True,
                )
            )
            if category:
                category_exists = (
                    db.query(models.Category)
                    .join(models.Category.shop)
                    .filter(
                        models.Shop.slug == shop,
                        models.Category.name == category,
                    )
                    .first()
                )
                if category_exists:
                    items_by_shop_category = (
                        items_by_shop.join(models.Item.category).filter(models.Category.name == category).all()
                    )

                    if items_by_shop_category:
                        return items_by_shop_category

            return items_by_shop.all()
        else:
            return all_items

    if category:
        items_by_category = (
            db.query(models.Item)
            .join(models.Item.category)
            .filter(
                models.Category.name == category,
                models.Item.is_approved == True,
                models.Item.is_available == True,
            )
            .all()
        )
        if items_by_category:
            return items_by_category

    return all_items
