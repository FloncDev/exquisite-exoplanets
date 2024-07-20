import os

from dotenv import find_dotenv, load_dotenv
from sqlmodel import create_engine, Session

load_dotenv(find_dotenv())

DATABASE_URL: str = os.environ["DATABASE"]
engine = create_engine(DATABASE_URL, echo=False)
session = Session(bind=engine, autoflush=True)


def get_session():
    try:
        yield session
    finally:
        session.close()
