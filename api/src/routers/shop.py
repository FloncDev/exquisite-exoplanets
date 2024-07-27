from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.company import CompanyRepresentation
from src.classes.pagination import ShopPagination
from src.classes.shop import ShopRepresentation
from src.db import get_session
from src.models import ShopItemCreate, ShopItemPublic, ShopItemPurchase, ShopItemPurchasedPublic, ShopItemUpdate

router = APIRouter()


@router.get("/shop")
async def get_shop(params: ShopPagination = Depends(), session: Session = Depends(get_session)) -> dict[str, Any]:
    """Get the items that are currently available in the shop to purchase.

    :param params: Pagination parameters.
    :param session: Database session.
    :return: Fetched shop items
    """
    return ShopRepresentation.fetch_shop(session=session, params=params)


@router.post("/shop", status_code=200)
async def create_shop_item(data: ShopItemCreate, session: Session = Depends(get_session)) -> dict[str, str]:
    """Create a new Item in the Shop.

    :param data: Shop Item data.
    :param session: Database session.
    :return: None
    """
    ShopRepresentation.create_item(session=session, data=data)
    return {"message": "Shop Item successfully created."}


@router.get("/shop/{item_id}")
async def get_shop_item(item_id: int, session: Session = Depends(get_session)) -> ShopItemPublic | None:
    """Get the target Shop Item from the database.

    :param item_id: ID of the Shop Item to fetch.
    :param session: Database session.
    :return: Fetched Shop Item
    """
    return ShopRepresentation.get_item(item_id=item_id, session=session).get_details()


@router.patch("/shop/{item_id}", status_code=200)
async def update_shop_item(
    item_id: int,
    data: ShopItemUpdate,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Update the target Shop Item with the given Data.

    :param item_id: ID of Shop Item to update.
    :param data: Data to update.
    :param session: Database session.
    :return: None
    """
    ShopRepresentation.update_item(session=session, data=data, item_id=item_id)
    return {"message": "Shop Item successfully updated."}


@router.post("/shop/{item_id}/buy", status_code=200)
async def company_purchase_shop_item(
    item_id: int, data: ShopItemPurchase, session: Session = Depends(get_session)
) -> ShopItemPurchasedPublic:
    """Target company purchases the target item.

    :param item_id: ID of Shop Item.
    :param data: Data of the Shop Item being bought.
    :param session: Database session.
    :return: None
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
        session=session, company_id=data.company_id
    )
    target_item: ShopRepresentation.ShopItemRepresentation = ShopRepresentation.get_item(
        session=session, item_id=item_id
    )
    return target_item.purchase_item(company=fetched_company.get_company(), data=data)
