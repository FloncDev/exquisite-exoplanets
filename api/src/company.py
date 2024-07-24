import datetime
import logging
from Planet import Planet
from Resource import Resource

company_logger = logging.getLogger(__name__)


class Company:

    def __init__(self, name: str, owner: str):
        self.__name = name
        self.__owner = owner
        self.__join_date = datetime.datetime.now()
        self.__balance = 0
        self.__planets = []
        self.__inventory = []
        self.__collectors = []

    def is_bankrupt(self):
        return self.__balance <= 0

    def get_name(self):
        return self.__name

    def get_owner(self):
        return self.__owner

    def get_join_date(self):
        return self.__join_date

    def get_balance(self):
        return self.__balance

    def get_planets(self):
        for planet in self.__planets:
            yield planet

    def get_collectors(self):
        for collector in self.__collectors:
            yield collector


