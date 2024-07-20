import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

load_dotenv(find_dotenv())

DATABASE_URL: str = os.environ["DATABASE"]
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autoflush=True, bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
