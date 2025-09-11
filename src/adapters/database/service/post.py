from typing import Optional

from ..dao.post import AbstractPostDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import PostDTO, PostRequestDTO

class InformationService:
    __slots__ = (
        "_common_dao",
        "_post_dao",
        "_current_post_id",
        "_current_post"
    )

    def __init__(
            self,
            post_dao: AbstractPostDAO,
            common_dao: AbstractCommonDAO,
            current_post_id: int
    ):
        self._post_dao = post_dao
        self._common_dao = common_dao
        self._current_post_id = current_post_id
        self._current_post: PostDTO | None = None

    async def get_post_by_id(self, post_id: int) -> PostDTO | None:
        result = await self._post_dao.get_post(post_id=post_id, sender_id=None, name=None)

        if not result:
            raise ValueError(f"Post with this post_id: {post_id} was not found.")

        return result

    async def get_post_by_name(self, sender_id: int, name: str) -> PostDTO | None:
        result = await self._post_dao.get_post(post_id=None, sender_id=sender_id, name=name)

        if not result:
            raise ValueError(f"Post with id: {sender_id} and name: {name} was not found.")

        return result

    async def get_posts(self, sender_id: int) -> list[PostDTO]:
        result = await self._post_dao.get_posts(sender_id=sender_id)

        return result

    async def get_current_post(self) -> PostDTO:
        if self._current_post:
            return self._current_post

        post = await self.get_post_by_id(self._current_post_id)

        if not post:
            raise ValueError("The post has not been found. ")

        self._current_post = post

        return post

    async def add_post(self, post: PostRequestDTO) -> PostDTO:
        result = await self._post_dao.add_post(post=post)
        await self._common_dao.commit()
        return result

    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO:
        result = await self._post_dao.update_post(post_id=post_id, post=post)
        await self._common_dao.commit()
        return result

    async def delete_post(self, post_id: int) -> bool:
        result = await self._post_dao.delete_post(post_id=post_id)
        await self._common_dao.commit()
        return result
