import logging

from ..dao.price import AbstractPriceDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import PriceDTO, PriceRequestDTO

from abc import ABC, abstractmethod

class AbstractPriceService(ABC):
    @abstractmethod
    async def add_price(self, name: str, price: int) -> PriceDTO | None:
        """
        Add price
        :param name: str
        :param price: int
        :return: PriceDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_price(self, name: str) -> PriceDTO | None:
        """
        Get price
        :param name: str
        :return: PriceDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def change_price(self, name: str, price: int) -> PriceDTO | None:
        """
        Change price
        :param name: str
        :param price: int
        :return: PriceDTO | None
        """
        raise NotImplementedError()

class PriceService(AbstractPriceService):
    def __init__(
            self,
            price_dao: AbstractPriceDAO,
            common_dao: AbstractCommonDAO
    ):
        self._price_dao = price_dao
        self._common_dao = common_dao
        self._logger = logging.getLogger(__name__)

    async def add_price(self, name: str, price: int) -> PriceDTO | None:
        try:
            result = await self._price_dao.add_price(name=name, price=price)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error adding price in database: %s", name, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def get_price(self, name: str) -> PriceDTO | None:
        try:
            return await self._price_dao.get_price(name=name)
        except Exception as e:
            self._logger.error("Error getting price from database: %s", name, e, exc_info=True)
            return None

    async def change_price(self, name: str, price: int) -> PriceDTO:
        try:
            result = await self._price_dao.change_price(name=name, price=price)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error changing price in database: %s", name, e, exc_info=True)
            await self._common_dao.rollback()
            return None