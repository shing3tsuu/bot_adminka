from abc import ABC, abstractmethod
import logging
from typing import Optional, List

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.dto import PriceDTO, PriceRequestDTO
from src.adapters.database.structures import Post, User, Price

class AbstractPriceDAO(ABC):
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
    async def change_price(self, name: str, price: int) ->  PriceDTO | None:
        """
        Change price
        :param name: str
        :param price: int
        :return: PriceDTO | None
        """
        raise NotImplementedError()

class PriceDAO(AbstractPriceDAO):
    __slots__ = ("_session", "_logger")

    def __init__(self, session: AsyncSession, logger: logging.Logger | None = None):
        self._session = session
        self._logger = logger

    async def add_price(self, name: str, price: int) -> PriceDTO | None:
        existing_price = await self._session.scalar(
            select(Price).where(
                Price.name == name
            )
        )
        if existing_price:
            raise ValueError(f"Price with name {price.name} already exists")
        stmt = (
            insert(Price)
            .values(
                name=name,
                price=price
            )
            .returning(Price)
        )
        result = await self._session.scalar(stmt)
        return PriceDTO.model_validate(result, from_attributes=True)

    async def get_price(self, name: str) -> PriceDTO | None:
        stmt = select(Price).where(
            Price.name == name
        )
        result = await self._session.scalar(stmt)
        if not result:
            return []
        return PriceDTO.model_validate(result, from_attributes=True)

    async def change_price(self, name: str, price: int) -> PriceDTO | None:
        stmt = (
            update(Price)
            .where(Price.name == name)
            .values(
                price=price
            )
            .returning(Price)
        )
        result = await self._session.scalar(stmt)
        return PriceDTO.model_validate(result, from_attributes=True)