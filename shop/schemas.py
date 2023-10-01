from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, field_validator


class UserRoleEnum(str, Enum):
    SHOP = "SHOP"
    CUSTOMER = "CUSTOMER"


class ShopOrderStatusEnum(str, Enum):
    NEW = "New"
    IN_PROCESS = "In Process"
    SENT = "Sent"


class UserBase(BaseModel):
    """
    Base Pydantic model for User. Includes common fields for create and update operations.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class UserProfileBase(BaseModel):
    """
    Base Pydantic model for UserProfile. Includes common fields for create and update operations.
    """

    profile_picture: Optional[UploadFile] = None
    phone_number: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    pin_code: Optional[str] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class UserCreate(UserBase):
    """
    Pydantic model for creating a new User.
    Inherits from UserBase and includes a hashed_password field for securely storing the user's password.
    """

    first_name: str
    last_name: str
    username: str
    email: EmailStr
    role: UserRoleEnum
    shop_name: Optional[str]
    password: str


class UserCompletePatch(UserBase, UserProfileBase):
    """
    Pydantic model for partially updating an existing User.
    Inherits from UserBase and makes all fields optional.
    """

    password: Optional[str] = None


class UserPatch(UserBase):
    """
    Pydantic model for partially updating an existing User.
    Inherits from UserBase and makes all fields optional.
    """

    password: Optional[str] = None


class UserInDB(UserBase):
    """
    Pydantic model for reading User from the database.
    Inherits from UserBase and includes additional fields like id, created_at, last_login, modified_at, and other attributes related to User.
    """

    id: int
    created_at: datetime
    last_login: datetime
    modified_at: datetime


class UserOut(BaseModel):
    """
    Pydantic model for sending User data in API responses.
    Inherits from UserInDB and is used for reading data from the API.
    """

    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    role: UserRoleEnum

    @field_validator("role")
    def validate_user_role(cls, value):
        if value not in UserRoleEnum:
            raise ValueError("Invalid user role")
        return value


class UserProfileCreate(UserProfileBase):
    """
    Pydantic model for creating a new UserProfile.
    Inherits from UserProfileBase and includes a field for specifying user_id to associate UserProfile with User.
    """

    user_id: int


class UserProfilePatch(UserProfileBase):
    """
    Pydantic model for updating an existing UserProfile.
    Inherits from UserProfileBase and does not include the user_id field, as it is not allowed to change the associated User.
    """

    pass


class UserProfileInDB(UserProfileBase):
    """
    Pydantic model for reading UserProfile from the database.
    Inherits from UserProfileBase and includes additional fields like id, user_id, created_at, and modified_at.
    """

    id: int
    created_at: datetime
    modified_at: datetime


class UserProfileOut(UserOut, UserProfileBase):
    """
    Pydantic model for sending UserProfile data in API responses.
    Inherits from UserProfileInDB and is used for reading data from the API.
    """

    profile_picture: Optional[UploadFile] = None
    phone_number: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    pin_code: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None


class ShopPatch(BaseModel):
    """
    Pydantic model for partially updating shop data.
    Represents the fields that can be updated in a shop.
    """

    shop_name: Optional[str] = None
    description: Optional[str] = None
    docs: Optional[UploadFile] = None
    avatar: Optional[UploadFile] = None
    cover_photo: Optional[UploadFile] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class ShopOut(ShopPatch):
    """
    Pydantic model for sending shop data in API responses.
    Inherits from ShopPatch and includes additional fields for reading shop data from the API.
    """

    id: int
    shop_name: str
    is_approved: bool
    created_at: datetime
    modified_at: Optional[datetime] = None


class CategoryBase(BaseModel):
    """
    Base Pydantic model for Category. Includes common fields for create and update operations.
    """

    name: Optional[str] = None
    is_available: Optional[bool] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class CategoryCreate(CategoryBase):
    """
    Pydantic model for creating a new Category.
    Inherits from CategoryBase and includes a field for specifying shop_id to associate Category with Shop.
    """

    name: str


class CategoryPatch(CategoryBase):
    """
    Pydantic model for partially updating an existing Category.
    Inherits from CategoryBase and makes all fields optional.
    """

    pass


class CategoryOut(CategoryBase):
    """
    Pydantic model for sending Category data in API responses.
    Inherits from CategoryBase and is used for reading data from the API.
    """

    id: int
    shop_id: int
    name: str
    slug: str
    is_available: bool


class ItemCreate(BaseModel):
    """
    Pydantic model for creating a new Item.
    """

    category_id: int
    name: str
    image: str
    title: str
    description: str
    price: float

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class ItemPatch(ItemCreate):
    """
    Base Pydantic model for Item. Includes common fields for create and update operations.
    """

    name: Optional[str] = None
    image: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None


class ItemReviewCreate(BaseModel):
    """
    Pydantic model for creating a new ItemReview.
    """

    stars: int
    comment: str

    @field_validator("stars")
    def validate_stars(cls, value):
        if value not in range(1, 6):
            raise ValueError("Invalid stars")
        return value

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class ItemReviewOut(ItemReviewCreate):
    """
    Pydantic model for sending ItemReview data in API responses.
    """

    id: int
    item_id: int
    user_id: int


class ItemOut(ItemCreate):
    """
    Pydantic model for sending Item data in API responses.
    Inherits from ItemBase and is used for reading data from the API.
    """

    id: int
    name: str
    title: str
    description: str
    slug: str
    average_rating: float
    is_available: bool
    created_at: datetime
    reviews: Optional[list[ItemReviewOut]] = None


class CartBase(BaseModel):
    """
    Base Pydantic model for Cart. Includes common fields for create and update operations.
    """

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class CartCreate(CartBase):
    """
    Pydantic model for creating a new Cart.
    Inherits from CartBase and includes a field for specifying user_id to associate Cart with User.
    """

    item_id: int
    quantity: int


class CartPatch(CartBase):
    """
    Pydantic model for partially updating an existing Cart.
    Inherits from CartBase and makes all fields optional.
    """

    quantity: Optional[int] = None


class CartOut(CartBase):
    """
    Pydantic model for sending Cart data in API responses.
    Inherits from CartBase and is used for reading data from the API.
    """

    item_id: int
    quantity: int
    price: float


class OrderBase(BaseModel):
    """
    Pydantic model for creating a new Order.
    Inherits from OrderBase and includes a field for specifying user_id to associate Order with User.
    """

    first_name: str
    last_name: str
    phone_number: str
    address: str
    country: str
    city: str
    pin_code: str

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class OrderOut(OrderBase):
    """
    Pydantic model for sending Order data in API responses.
    """

    id: int
    billing_status: bool
    total_paid: float
    created_at: datetime


class OrderItemCreate(BaseModel):
    """
    Pydantic model for creating a new OrderItem.
    Inherits from OrderItemBase and includes a field for specifying order_id to associate OrderItem with Order.
    """

    item_id: int
    order_id: int
    quantity: int

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class OrderItemOut(OrderItemCreate):
    """
    Pydantic model for sending OrderItem data in API responses.
    Inherits from OrderItemBase and is used for reading data from the API.
    """

    id: int
    price: float
    quantity: int
    created_at: datetime


class ShopOrderBase(BaseModel):
    """
    Pydantic model for creating a new ShopOrder.
    Inherits from ShopOrderBase and includes a field for specifying order_id to associate ShopOrder with Order.
    """

    user_id: int
    order_id: int
    shop_id: int
    status: ShopOrderStatusEnum

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class ShopOrderPatch(BaseModel):
    """
    Pydantic model for partially updating an existing ShopOrder.
    Inherits from ShopOrderBase and makes all fields optional.
    """

    status: ShopOrderStatusEnum

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"


class ShopOrderOut(ShopOrderBase):
    """
    Pydantic model for sending ShopOrder data in API responses.
    Inherits from ShopOrderBase and is used for reading data from the API.
    """

    id: int
    status: ShopOrderStatusEnum
    total_paid: int
    billing_status: bool
    created_at: datetime


class NewsLetterBase(BaseModel):
    """
    Base Pydantic model for NewsLetter. Includes common fields for create and update operations.
    """

    email: EmailStr

    class Config:
        validate_assignment = True
        extra = "forbid"


class NewsLetterOut(NewsLetterBase):
    """
    Pydantic model for sending NewsLetter data in API responses.
    """

    id: int
    is_active: bool
    created_at: datetime
