from .database import Base
from passlib.context import CryptContext
from .schemas import UserRoleEnum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


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
