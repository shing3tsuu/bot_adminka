from typing import Optional

from ..dao.user import AbstractUserDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import UserDTO, UserRequestDTO
from src.adapters.encryption import AbstractCodeEncoder


class UserService:
    __slots__ = (
        "_common_dao",
        "_user_dao",
        "_current_user",
        "_current_user_tg_id"
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

    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        return await self._user_dao.get_user(user_id=user_id)

    async def get_user_by_tg_id(self, user_tg_id: int) -> UserDTO | None:
        return await self._user_dao.get_user(user_tg_id=user_tg_id)

    async def get_current_user(self) -> UserDTO:
        if self._current_user:
            return self._current_user

        user = await self.get_user_by_tg_id(self._current_user_tg_id)

        if not user:
            raise ValueError("The user has not been found. ")

        self._current_user = user

        return user

    async def add_user(self, user: UserRequestDTO) -> UserDTO:
        result = await self._user_dao.add_user(user=user)
        await self._common_dao.commit()
        return result

    async def change_user_data(self, user: UserRequestDTO) -> UserDTO:
        result = await self._user_dao.change_user_data(user=user)
        await self._common_dao.commit()
        return result

    async def delete_user(self, user: UserRequestDTO) -> bool:
        result = await self._user_dao.delete_user(user=user)
        await self._common_dao.commit()
        return result

    async def upsert_user(self, user: UserRequestDTO) -> UserDTO:
        existing_user = await self.get_user_by_tg_id(user.tg_id)

        if existing_user:
            return await self.change_user_data(user)
        else:
            return await self.add_user(user)