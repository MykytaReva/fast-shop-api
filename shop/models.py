from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base
from .schemas import UserRoleEnum


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
    shop = relationship("Shop", back_populates="user", uselist=False, cascade="all, delete-orphan")

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
    state = Column(String(40), nullable=True)
    pin_code = Column(String(15), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    modified_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship with User model (One-to-One)
    user = relationship("User", back_populates="profile", uselist=False)


# TODO add unique slug with checks.
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
    # TODO change is_approved/is_available for category/shop/item to False by default
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("Category", back_populates="shop")
    items = relationship("Item", back_populates="shop")
    user = relationship("User", back_populates="shop", uselist=False)


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
    item_images = relationship("ItemImage", back_populates="item")


class ItemImage(Base):
    __tablename__ = "item_image"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("item.id"))

    image = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    item = relationship("Item", back_populates="item_images")
