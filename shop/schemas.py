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
    shop_name: Optional[str] = None
    docs: Optional[str] = None
    avatar: Optional[UploadFile] = None
    cover_photo: Optional[UploadFile] = None

    class Config:
        from_attributes = True


# TODO add all shop's categories field
class ShopOut(BaseModel):
    id: int
    shop_name: str
    docs: Optional[str] = None
    avatar: Optional[str] = None
    cover_photo: Optional[str] = None
    is_approved: bool
    created_at: datetime
    modified_at: Optional[datetime] = None

    class Config:
        from_attributes = True
