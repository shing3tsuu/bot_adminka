from typing import Optional
from abc import ABC, abstractmethod
import logging

from sqlalchemy import select, delete, insert, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.dto import UserRequestDTO, UserDTO
from src.adapters.database.structures import User


class AbstractUserDAO(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int | None = None, user_tg_id: int | None = None) -> UserDTO | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_surname_name_patronymic(self, user: UserRequestDTO) -> UserDTO | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_users_by_name(self, user: UserRequestDTO) -> list[UserDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def get_users_by_surname(self, user: UserRequestDTO) -> list[UserDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def add_user(self, user: UserRequestDTO) -> UserDTO:
        raise NotImplementedError()

    @abstractmethod
    async def change_user_data(self, user: UserRequestDTO) -> UserDTO:
        raise NotImplementedError()

    @abstractmethod
    async def delete_user(self, user: UserRequestDTO) -> bool:
        raise NotImplementedError()


class UserDAO(AbstractUserDAO):
    __slots__ = ("_session", "_logger")

    def __init__(self, session: AsyncSession, logger: logging.Logger | None = None):
        self._session = session
        self._logger = logger or logging.getLogger(__name__)

    async def get_user_by_id(self, user_id: int | None = None, user_tg_id: int | None = None) -> UserDTO | None:
        if not user_id and not user_tg_id:
            raise ValueError("One of the parameters (user_id or user_tg_id) must be passed")

        try:
            stmt = select(User)
            if user_id:
                stmt = stmt.where(User.id == user_id)
            if user_tg_id:
                stmt = stmt.where(User.tg_id == user_tg_id)

            result = await self._session.scalar(stmt)

            return UserDTO.model_validate(result, from_attributes=True) if result else None

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_user: {e}")
            raise

    async def get_user_by_surname_name_patronymic(self, user: UserRequestDTO) -> UserDTO | None:
        try:
            stmt = select(User).where(
                func.lower(User.surname) == func.lower(user.surname),
                func.lower(User.name) == func.lower(user.name),
                func.lower(User.patronymic) == func.lower(user.patronymic)
            )
            result = await self._session.scalar(stmt)

            return UserDTO.model_validate(result, from_attributes=True) if result else None

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_user_by_surname_name_patronymic: {e}")
            raise

    async def get_users_by_name(self, user: UserRequestDTO) -> list[UserDTO]:
        try:
            stmt = select(User).where(
                User.name.ilike(f"%{user.name}%"),
            )
            result = await self._session.scalars(stmt)

            return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_users_by_name: {e}")
            raise

    async def get_users_by_surname(self, user: UserRequestDTO) -> list[UserDTO]:
        try:
            stmt = select(User).where(
                User.surname.ilike(f"%{user.surname}%"),
            )
            result = await self._session.scalars(stmt)

            return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_users_by_surname: {e}")
            raise

    async def add_user(self, user: UserRequestDTO) -> UserDTO:
        try:
            existing_user = await self._session.scalar(
                select(User).where(User.tg_id == user.tg_id)
            )

            if existing_user:
                raise ValueError(f"User with tg_id {user.tg_id} already exists")

            stmt = (
                insert(User)
                .values(**user.model_dump())
                .returning(User)
            )
            result = await self._session.scalar(stmt)
            return UserDTO.model_validate(result, from_attributes=True)

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in add_user: {e}")
            raise

    async def change_user_data(self, user: UserRequestDTO) -> UserDTO:
        try:
            stmt = (
                update(User)
                .where(User.tg_id == user.tg_id)
                .values(**user.model_dump())
                .returning(User)
            )
            result = await self._session.scalar(stmt)

            if not result:
                raise ValueError(f"User with tg_id {user.tg_id} not found")

            return UserDTO.model_validate(result, from_attributes=True)

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in change_user_data: {e}")
            raise

    async def delete_user(self, user: UserRequestDTO) -> bool:
        try:
            stmt = delete(User).where(User.tg_id == user.tg_id)
            result = await self._session.execute(stmt)
            return result.rowcount > 0

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in delete_user: {e}")
            raise