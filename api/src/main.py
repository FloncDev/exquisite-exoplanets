from fastapi import FastAPI
from sqlmodel import SQLModel
from src.db import engine
from uvicorn import run

from .routers import company, shop, user

SQLModel.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(company.router)
app.include_router(user.router)
app.include_router(shop.router)


def main() -> None:
    """Create the database tables."""
    run("src.main:app", reload=True)
