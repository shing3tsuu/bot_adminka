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
        """
        Get user by id or tg_id
        :param user_id:
        :param user_tg_id:
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def search_users_by_fio(self, search_string: str) -> list[UserDTO]:
        """
        Search users by fio
        :param search_string:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_users_by_name(self, user: UserRequestDTO) -> list[UserDTO]:
        """
        Get users by name
        :param user:
        :return:
        """
        raise NotImplementedError()

    async def get_users_by_surname(self, user: UserRequestDTO) -> list[UserDTO]:
        """
        Get users by surname
        :param user:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_all_users(self) -> list[UserDTO]:
        """
        Get all users
        :return: list[UserDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def add_user(self, user: UserRequestDTO) -> UserDTO | None:
        """
        Add user
        :param user: UserRequestDTO
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def change_user_data(self, user: UserRequestDTO) -> UserDTO | None:
        """
        Change user data
        :param user_id: int | None
        :param user: UserRequestDTO
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def approve_user(self, user_id: int) -> bool:
        """
        Approve user
        :param user_id: int
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_user(self, user: UserRequestDTO) -> bool:
        """
        Delete user
        :param user: UserRequestDTO
        :return: bool
        """
        raise NotImplementedError()

class UserDAO(AbstractUserDAO):
    __slots__ = ("_session", "_logger")

    def __init__(self, session: AsyncSession, logger: logging.Logger | None = None):
        self._session = session
        self._logger = logger or logging.getLogger(__name__)

    async def get_user_by_id(self, user_id: int | None = None, user_tg_id: int | None = None) -> UserDTO | None:
        if not user_id and not user_tg_id:
            raise ValueError("One of the parameters (user_id or user_tg_id) must be passed")
        stmt = select(User)
        if user_id:
            stmt = stmt.where(User.id == user_id)
        if user_tg_id:
            stmt = stmt.where(User.tg_id == user_tg_id)
        result = await self._session.scalar(stmt)
        return UserDTO.model_validate(result, from_attributes=True) if result else None

    async def search_users_by_fio(self, search_string: str) -> list[UserDTO]:
        search_terms = search_string.strip().split()

        conditions = []
        for term in search_terms:
            term_condition = (
                    User.surname.ilike(f"%{term}%") |
                    User.name.ilike(f"%{term}%") |
                    User.patronymic.ilike(f"%{term}%")
            )
            conditions.append(term_condition)

        if conditions:
            stmt = select(User).where(*conditions)
        else:
            stmt = select(User)

        result = await self._session.scalars(stmt)
        return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

    async def get_users_by_name(self, user: UserRequestDTO) -> list[UserDTO]:
        stmt = select(User).where(
            User.name.ilike(f"%{user.name}%"),
        )
        result = await self._session.scalars(stmt)
        return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

    async def get_users_by_surname(self, user: UserRequestDTO) -> list[UserDTO]:
        stmt = select(User).where(
            User.surname.ilike(f"%{user.surname}%"),
        )
        result = await self._session.scalars(stmt)
        return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

    async def get_all_users(self) -> list[UserDTO]:
        stmt = select(User)
        result = await self._session.scalars(stmt)
        return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

    async def get_unapproved_users(self) -> list[UserDTO]:
        stmt = select(User).where(User.is_approved == False)
        result = await self._session.scalars(stmt)
        return [UserDTO.model_validate(user, from_attributes=True) for user in result.all()]

    async def add_user(self, user: UserRequestDTO) -> UserDTO:
        existing_user = await self._session.scalar(select(User).where(User.tg_id == user.tg_id))
        if existing_user:
            raise ValueError(f"User with tg_id {user.tg_id} already exists")
        stmt = (
            insert(User)
            .values(**user.model_dump())
            .returning(User)
        )
        result = await self._session.scalar(stmt)
        return UserDTO.model_validate(result, from_attributes=True)

    async def change_user_data(self, user: UserRequestDTO) -> UserDTO | None:
        stmt = (
            update(User)
            .where(User.tg_id == user.tg_id)
            .values(**user.model_dump(exclude_unset=True))
            .returning(User)
        )
        result = await self._session.scalar(stmt)
        if not result:
            raise ValueError(f"User with tg_id {user.tg_id} not found")
        return UserDTO.model_validate(result, from_attributes=True)

    async def approve_user(self, user_id: int) -> bool:
        stmt = update(User).where(User.id == user_id).values(is_approved=True).returning(User)
        result = await self._session.scalar(stmt)
        if result:
            return True
        else:
            return False

    async def delete_user(self, user: UserRequestDTO) -> bool:
        stmt = delete(User).where(User.tg_id == user.tg_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0