import logging

from ..dao.user import AbstractUserDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import UserDTO, UserRequestDTO

from abc import ABC, abstractmethod

class AbstractUserService(ABC):
    @abstractmethod
    async def get_all_users(self) -> list[UserDTO]:
        """
        Get all users from database
        :return: list[UserDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def search_users_by_fio(self, search_string: str) -> list[UserDTO]:
        """
        Search users by fio
        :param search_string: str
        :return: list[UserDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def approve_user(self, tg_id: int) -> bool:
        """
        Approve user
        :param tg_id:
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unapproved_users(self) -> list[UserDTO]:
        """
        Get unapproved users
        :return: list[UserDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        """
        Get user by id
        :param user_id:
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_tg_id(self, user_tg_id: int) -> UserDTO | None:
        """
        Get user by tg_id
        :param user_tg_id:
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_current_user(self) -> UserDTO | None:
        """
        Get current user
        :return: UserDTO | None
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
        :param user:
        :return: UserDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_user(self, user: UserRequestDTO) -> bool:
        """
        Delete user
        :param user:
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    async def upsert_user(self, user: UserRequestDTO) -> UserDTO | None:
        """
        Upsert user
        :param user:
        :return: UserDTO | None
        """
        raise NotImplementedError()

class UserService(AbstractUserService):
    __slots__ = (
        "_common_dao",
        "_user_dao",
        "_current_user",
        "_current_user_tg_id",
        "_logger"
    )

    def __init__(
            self,
            user_dao: AbstractUserDAO,
            common_dao: AbstractCommonDAO,
            current_user_tg_id: int
    ):
        self._user_dao = user_dao
        self._common_dao = common_dao
        self._current_user_tg_id = current_user_tg_id
        self._current_user: UserDTO | None = None

        self._logger = logging.getLogger(__name__)

    async def get_all_users(self) -> list[UserDTO]:
        try:
            return await self._user_dao.get_all_users()
        except Exception as e:
            self._logger.error("Error getting all users in database: %s", e, exc_info=True)
            return []

    async def search_users_by_fio(self, search_string: str) -> list[UserDTO]:
        try:
            return await self._user_dao.search_users_by_fio(search_string=search_string)
        except Exception as e:
            self._logger.error("Error searching users by fio in database: %s", e, exc_info=True)
            return []

    async def approve_user(self, user_id: int) -> bool:
        try:
            result = await self._user_dao.approve_user(user_id=user_id)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error approving user with id %s in database: %s", user_id, e, exc_info=True)
            await self._common_dao.rollback()
            return False

    async def get_unapproved_users(self) -> list[UserDTO]:
        try:
            return await self._user_dao.get_unapproved_users()
        except Exception as e:
            self._logger.error("Error getting unapproved users in database: %s", e, exc_info=True)
            return []

    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        try:
            return await self._user_dao.get_user_by_id(user_id=user_id)
        except Exception as e:
            self._logger.error("Error getting user by id %s in database: %s", user_id, e, exc_info=True)
            return None

    async def get_user_by_tg_id(self, user_tg_id: int) -> UserDTO | None:
        try:
            return await self._user_dao.get_user_by_id(user_tg_id=user_tg_id)
        except Exception as e:
            self._logger.error("Error getting user by tg_id %s in database: %s", user_tg_id, e, exc_info=True)
            return None

    async def get_current_user(self) -> UserDTO | None:
        try:
            if self._current_user:
                return self._current_user
            user = await self.get_user_by_tg_id(self._current_user_tg_id)
            if not user:
                raise ValueError("The user has not been found. ")
            self._current_user = user
            return user
        except Exception as e:
            self._logger.error("Error getting current user in database: %s", e, exc_info=True)
            return None

    async def add_user(self, user: UserRequestDTO) -> UserDTO | None:
        try:
            result = await self._user_dao.add_user(user=user)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error adding user in database: %s", e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def change_user_data(self, user: UserRequestDTO) -> UserDTO | None:
        try:
            result = await self._user_dao.change_user_data(user=user)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error changing user data in database: %s", e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def delete_user(self, user: UserRequestDTO) -> bool:
        try:
            result = await self._user_dao.delete_user(user=user)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error deleting user in database: %s", e, exc_info=True)
            await self._common_dao.rollback()
            return False

    async def upsert_user(self, user: UserRequestDTO) -> UserDTO | None:
        existing_user = await self.get_user_by_tg_id(user.tg_id)
        if existing_user:
            return await self.change_user_data(user)
        else:
            return await self.add_user(user)