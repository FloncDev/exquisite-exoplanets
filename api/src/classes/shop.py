from typing import Any, Self

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, desc, not_, select
from src.classes.pagination import Paginate, ShopPagination
from src.models import (
    Company,
    Inventory,
    ShopItem,
    ShopItemCreate,
    ShopItemPublic,
    ShopItemPurchase,
    ShopItemUpdate,
)


class ShopRepresentation:
    """Class that represents the `shop`."""

    class ShopItemRepresentation:
        """Class that represents a single `item` found in the Shop."""

        def __init__(self, session: Session, shop_item: ShopItem) -> None:
            self.session: Session = session
            self.shop_item: ShopItem = shop_item

        @classmethod
        def create_shop_item(cls, session: Session, data: ShopItemCreate) -> Self:
            """Create a new Item to be added to the Shop.

            :param session: Database session.
            :param data: Shop Item data.
            :return: Instance with the newly created Shop Item.
            """
            # Checking that an Item with the same name does not exist.
            # If so, raise exception.
            fetched_shop_item: ShopItem | None = session.exec(
                select(ShopItem).where(ShopItem.name == data.name)
            ).first()

            if fetched_shop_item is not None:
                raise HTTPException(status_code=409, detail="Shop Item already exists.")

            new_shop_item: ShopItem = ShopItem(**data.model_dump())

            # If the quantity is 0, then it is not purchasable
            if new_shop_item.available_quantity == 0:
                new_shop_item.is_disabled = True

            session.add(new_shop_item)

            try:
                session.commit()
                session.refresh(new_shop_item)

            except SQLAlchemyError as ex:
                print(ex)
                session.rollback()
                raise HTTPException(status_code=400, detail="Unable to create new Shop Item.") from None

            return cls(session=session, shop_item=new_shop_item)

        @classmethod
        def fetch_shop_item(cls, session: Session, shop_item_id: int) -> Self:
            """Fetch the target Shop Item from the database.

            :param session: Database session.
            :param shop_item_id: ID of Shop Item to fetch.
            :return: Instance with fetched Shop Item.
            """
            fetched_shop_item: ShopItem | None = session.exec(
                select(ShopItem).where(ShopItem.id == shop_item_id)
            ).first()

            if fetched_shop_item is None:
                raise HTTPException(status_code=404, detail="Shop Item not found.")

            return cls(session=session, shop_item=fetched_shop_item)

        @classmethod
        def fetch_shop_items(cls, session: Session, params: ShopPagination) -> dict[str, Any]:
            """Get the Items from the Shop, with pagination.

            :param session: Database session.
            :param params: Pagination parameters.
            :return: Fetched Shop Items.
            """
            q: Any = select(ShopItem)

            # Get by status
            if params.is_disabled is not None:
                q = q.where(ShopItem.is_disabled) if params.is_disabled else q.where(not_(ShopItem.is_disabled))

            # Sort by given type
            match params.sort_by:
                case "price":
                    q = q.order_by(desc(ShopItem.price)) if not params.ascending else q.order_by(ShopItem.price)

                case "quantity":
                    q = (
                        q.order_by(desc(ShopItem.available_quantity))
                        if not params.ascending
                        else q.order_by(ShopItem.available_quantity)
                    )

                case "name":
                    q = q.order_by(desc(ShopItem.name)) if not params.ascending else q.order_by(ShopItem.name)

                case _:
                    pass

            paginator: Paginate = Paginate(query=q, session=session, params=params)

            res: list[ShopItemPublic] = [ShopItemPublic.model_validate(x) for x in paginator.get_data()]

            if not res:
                raise HTTPException(status_code=404, detail="Shop Items not found.")

            paginator.add_data({"shop_items": res})
            return paginator.get_page()

        def purchase_item(self, company: Company, data: ShopItemPurchase) -> None:
            """Add purchased Item to the Company's inventory.

            :param data: Data on Shop Item purchase.
            :param company: Target company purchasing the Shop Item.
            :return: None
            """
            # Check if the item is not disabled.
            if self.shop_item.is_disabled:
                raise HTTPException(status_code=400, detail="Cannot purchase item; disabled.")

            # Check if the Company is not bankrupt
            if company.is_bankrupt:
                raise HTTPException(status_code=403, detail="Company is bankrupt; cannot purchase.")

            # Check that the Item has stock
            if self.shop_item.available_quantity < 1:
                raise HTTPException(status_code=403, detail="No available items to purchase.")

            # Check that the Company is not buying more than what is available.
            if self.shop_item.available_quantity < data.purchase_quantity:
                raise HTTPException(status_code=400, detail="Cannot purchase more than what is available.")

            # Check that the User can purchase the Item.
            purchase_cost: float = self.shop_item.price * data.purchase_quantity
            if purchase_cost > company.networth:
                raise HTTPException(status_code=400, detail="Cannot purchase; insufficient funds.")

            # Purchase the item(s)
            company_inventory: list[Inventory] = company.inventory

            if len(company_inventory) == 0:
                # Add Item to Company Inventory
                if company.id is not None and self.shop_item.id is not None:
                    new_inventory_item: Inventory = Inventory(
                        item_id=self.shop_item.id,
                        company_id=company.id,
                        stock=data.purchase_quantity,
                        total_amount_spent=purchase_cost,
                    )
                    self.session.add(new_inventory_item)

            else:
                # Check if the items is present, if not, add it.
                target_item: Inventory | None = next(
                    filter(lambda x: x.item_id == self.shop_item.id, company_inventory), None
                )

                if target_item is None:
                    # Create Inventory entry
                    if company.id is not None and self.shop_item.id is not None:
                        new_inventory_item: Inventory = Inventory(
                            item_id=self.shop_item.id,
                            company_id=company.id,
                            stock=data.purchase_quantity,
                            total_amount_spent=purchase_cost,
                        )
                        self.session.add(new_inventory_item)

                else:
                    # Update inventory
                    target_item.stock += data.purchase_quantity
                    target_item.total_amount_spent += self.shop_item.price
                    self.session.add(target_item)

            # Update the Shop Item that was purchased
            self.shop_item.available_quantity -= data.purchase_quantity
            if self.shop_item.available_quantity < 1:
                self.shop_item.is_disabled = True
            self.session.add(self.shop_item)

            # Update the Company
            company.networth -= purchase_cost
            if company.networth < 1:
                company.is_bankrupt = True
                self.session.add(company)

            # Save changes
            try:
                self.session.commit()

            except SQLAlchemyError:
                self.session.rollback()
                raise HTTPException(status_code=400, detail="Unable to purchase Shop Item.") from None

        def get_shop_item(self) -> ShopItem:
            """Get the Shop Item bound to the instance.

            :return: Bound Shop Item.
            """
            return self.shop_item

        def get_details(self) -> ShopItemPublic:
            """Get the details of the Shop Item.

            :return: Shop Item details.
            """
            return ShopItemPublic.model_validate(self.shop_item)

        def update(self, data: ShopItemUpdate) -> None:
            """Update the details of the Shop Item.

            :param data: Data to update.
            :return: None
            """
            has_changed: bool = False

            if data.name is not None:
                self.shop_item.name = data.name
                has_changed = True

            if data.quantity is not None:
                self.shop_item.available_quantity = data.quantity
                has_changed = True

            if data.price is not None:
                self.shop_item.price = data.price
                has_changed = True

            if data.is_disabled is not None:
                self.shop_item.is_disabled = data.is_disabled
                has_changed = True

            if has_changed:
                try:
                    self.session.add(self.shop_item)
                    self.session.commit()
                    self.session.refresh(self.shop_item)

                except SQLAlchemyError:
                    raise HTTPException(status_code=500, detail="Unable to update Shop Item.") from None

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    @classmethod
    def fetch_shop(cls, session: Session, params: ShopPagination) -> dict[str, Any]:
        """Get the current Shop.

        :param session: Database session.
        :param params: Pagination parameters.
        :return: Fetch Shop Items
        """
        return ShopRepresentation.ShopItemRepresentation.fetch_shop_items(session=session, params=params)

    @classmethod
    def create_item(cls, session: Session, data: ShopItemCreate) -> None:
        """Create a new Item in the Shop.

        :param session: Database session.
        :param data: Shop Item data.
        :return: None
        """
        ShopRepresentation.ShopItemRepresentation.create_shop_item(session=session, data=data)

    @classmethod
    def update_item(cls, session: Session, data: ShopItemUpdate, item_id: int) -> None:
        """Update the details of a Shop Item.

        :param session: Database session.
        :param data: Shop Item data to update.
        :param item_id: ID of Shop Item to update.
        :return: None
        """
        target_item: ShopRepresentation.ShopItemRepresentation = (
            ShopRepresentation.ShopItemRepresentation.fetch_shop_item(session=session, shop_item_id=item_id)
        )
        target_item.update(data=data)

    @classmethod
    def get_item(cls, session: Session, item_id: int) -> "ShopRepresentation.ShopItemRepresentation":
        """Get the Shop Item from the database.

        :param session: Database session.
        :param item_id: ID of Shop Item to get.
        :return: Fetched Shop Item.
        """
        return ShopRepresentation.ShopItemRepresentation.fetch_shop_item(session=session, shop_item_id=item_id)
