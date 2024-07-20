# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

import math
from enum import IntEnum
from typing import Any, Dict, List, Sequence

from sqlalchemy import Row, RowMapping
from sqlmodel import Session


class PaginationDefaults(IntEnum):
    PAGE = 1
    LIMIT = 10


class Pagination:
    """Base class for pagination"""

    def __init__(self, page: int = PaginationDefaults.PAGE.value, limit: int = PaginationDefaults.LIMIT.value):
        self.page: int = page
        self.limit: int = limit

    def as_dict(self) -> Dict[str, Any]:
        """Get the params as a dict."""
        res: Dict[str, Any] = {"page": self.page, "limit": self.limit}

        return res


class CompanyPagination(Pagination):
    """Pagination for getting Companies"""

    def __init__(
        self,
        page: int = PaginationDefaults.PAGE.value,
        limit: int = PaginationDefaults.LIMIT.value,
        *,
        ascending: bool = False,
    ):
        super().__init__(page=page, limit=limit)
        self.ascending: bool | None = ascending

    def as_dict(self) -> Dict[str, Any]:
        """Get the params as a dict."""
        return super().as_dict()


class Paginate:
    """Paginate response."""

    def __init__(self, query: Any, params: Any, session: Session):
        self.query: Any = query
        self.session: Session = session
        self.params: Any = params
        self.data: List[Dict[str, Any]] = []

        # Determining necessary variables
        self.entry_count: int = len(self.session.exec(self.query).all())  # type: ignore
        self.page_count: int = 1 if self.params.limit < 1 else math.ceil(self.entry_count / self.params.limit)

    def get_data(self) -> Sequence[Row[Any] | RowMapping | Any]:
        """
        Method to get the data from the given query according to the pagination parameters

        :return: Data from the given query.
        """
        return self.session.exec(
            self.query.offset((self.params.page - 1) * self.params.limit).limit(self.params.limit)
        ).all()

    def add_data(self, data: Dict[str, Any]) -> None:
        """
        Method to add data to the Page.

        :param data: Data to add.
        :return: None
        """
        self.data.append(data)

    def get_page(self) -> Dict[str, Any]:
        """
        Get the current page.

        :return: Current page results.
        """
        res: Dict[str, Any] = self.params.as_dict()
        res["page_count"] = self.page_count
        res["entry_count"] = self.entry_count

        # Adding results
        for d in self.data:
            res.update(d)

        return res
