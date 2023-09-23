from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from shop import constants

SQLALCHEMY_DATABASE_URL = f"postgresql://{constants.POSTGRES_USER}:{constants.POSTGRES_PASSWORD}@{constants.POSTGRES_HOST}/{constants.POSTGRES_DB}"

# SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"
SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
test_engine = create_engine(SQLALCHEMY_DATABASE_URL_TEST, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()
