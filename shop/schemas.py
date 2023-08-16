from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, field_validator


class UserRoleEnum(str, Enum):
    SHOP = "SHOP"
    CUSTOMER = "CUSTOMER"


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
        extra = "allow"


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
    state: Optional[str] = None
    pin_code: Optional[str] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "allow"


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
    is_staff: bool
    is_active: bool
    is_superuser: bool
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
    state: Optional[str] = None
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
    docs: Optional[str] = None
    avatar: Optional[UploadFile] = None
    cover_photo: Optional[UploadFile] = None

    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "allow"


# TODO add all shop's categories field
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
        extra = "allow"


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
        extra = "allow"


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


class ItemOut(ItemCreate):
    """
    Pydantic model for sending Item data in API responses.
    Inherits from ItemBase and is used for reading data from the API.
    """

    id: int
    name: str
    slug: str
    is_approved: bool
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
