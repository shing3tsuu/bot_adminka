from typing import Optional

from ..dao.price import AbstractPriceDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import PriceDTO, PriceRequestDTO

class PriceService:
    def __init__(
            self,
            price_dao: AbstractPriceDAO,
            common_dao: AbstractCommonDAO
    ):
        self._price_dao = price_dao
        self._common_dao = common_dao

    async def add_price(self, name: str, price: int) -> PriceDTO:
        result = await self._price_dao.add_price(name=name, price=price)
        await self._common_dao.commit()
        return result

    async def get_price(self, name: str) -> PriceDTO | None:
        return await self._price_dao.get_price(name=name)

    async def change_price(self, name: str, price: int) -> PriceDTO:
        result = await self._price_dao.change_price(name=name, price=price)
        await self._common_dao.commit()
        return result