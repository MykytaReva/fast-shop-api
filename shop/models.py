from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from shop.database import Base
from shop.schemas import ShopOrderStatusEnum, UserRoleEnum

association_table = Table(
    "wish_list",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("item_id", ForeignKey("item.id"), primary_key=True),
)


class User(Base):
    """
    SQLAlchemy model for User.
    Represents the 'users' table in the database.
    User model can be either a Shop or a regular Customer
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    _password = Column("password", String(128), nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.CUSTOMER)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    modified_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    shop = relationship("Shop", uselist=False, back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    shop_orders = relationship("ShopOrder", back_populates="user")

    items = relationship("Item", secondary=association_table, back_populates="users")
    item_reviews = relationship("ItemReview", back_populates="user")

    # Property to access the hashed password
    @property
    def password(self):
        return self._password

    # Method to set the hashed password
    def set_password(self, password):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._password = pwd_context.hash(password)


class UserProfile(Base):
    """
    SQLAlchemy model for UserProfile.
    Represents the 'user_profiles' table in the database.
    UserProfile connected to User model.
    Provides additional personal information and base-delivery address.
    """

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)

    profile_picture = Column(String(255), nullable=True)
    phone_number = Column(String(14), nullable=True)
    dob = Column(DateTime, nullable=True)

    address = Column(String(250), nullable=True)
    country = Column(String(16), nullable=True)
    city = Column(String(16), nullable=True)
    pin_code = Column(String(15), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    modified_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship with User model (One-to-One)
    user = relationship("User", back_populates="profile", uselist=False)


class Shop(Base):
    """
    SQLAlchemy model for Shop.
    Represents the 'shop' table in the database.
    Shop is created if user choose role shop only.
    """

    __tablename__ = "shop"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    shop_name = Column(String(50), unique=True, index=True)
    docs = Column(String)
    avatar = Column(String(255), nullable=True)
    cover_photo = Column(String(255), nullable=True)
    description = Column(Text)

    slug = Column(String, unique=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", back_populates="shop", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="shop", cascade="all, delete-orphan")
    user = relationship("User", back_populates="shop", uselist=False)
    shop_orders = relationship("ShopOrder", back_populates="shop", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shop.id"))

    name = Column(String(100))
    slug = Column(String, unique=True)
    is_available = Column(Boolean, default=True)

    # Relationships
    shop = relationship("Shop", back_populates="categories")
    items = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shop.id"))
    category_id = Column(Integer, ForeignKey("category.id"))

    name = Column(String(55))
    image = Column(String)
    title = Column(String(200))
    description = Column(Text)
    price = Column(Float(precision=2))

    slug = Column(String, unique=True)
    is_approved = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="items")
    shop = relationship("Shop", back_populates="items")
    cart_items = relationship("CartItem", back_populates="item", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="item", cascade="all, delete-orphan")

    users = relationship("User", secondary=association_table, back_populates="items")
    reviews = relationship("ItemReview", back_populates="item", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("item.id"))

    quantity = Column(Integer, default=1)
    price = Column(Float(precision=2))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="cart_items", uselist=False)
    item = relationship("Item", back_populates="cart_items")


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(14), nullable=True)
    address = Column(String(250), nullable=True)
    country = Column(String(16), nullable=True)
    city = Column(String(16), nullable=True)
    pin_code = Column(String(15), nullable=True)
    # TODO change default to False
    billing_status = Column(Boolean, default=True)
    order_key = Column(String(200))
    total_paid = Column(Float(precision=2))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shop_orders = relationship("ShopOrder", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    item_id = Column(Integer, ForeignKey("item.id"))

    price = Column(Float(precision=2))
    quantity = Column(Integer, default=1)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")


class ShopOrder(Base):
    __tablename__ = "shop_order"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shop.id"))
    order_id = Column(Integer, ForeignKey("order.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    # TODO change default to False
    billing_status = Column(Boolean, default=True)
    total_paid = Column(Float(precision=2))
    status = Column(Enum(ShopOrderStatusEnum), default=ShopOrderStatusEnum.NEW)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now())

    # Relationships
    shop = relationship("Shop", back_populates="shop_orders")
    order = relationship("Order", back_populates="shop_orders")
    user = relationship("User", back_populates="shop_orders")


class NewsLetter(Base):
    __tablename__ = "newsletter"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(100), unique=True)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ItemReview(Base):
    __tablename__ = "item_review"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("item.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    stars = Column(Integer)
    comment = Column(Text)

    item = relationship("Item", back_populates="reviews")
    user = relationship("User", back_populates="item_reviews")
