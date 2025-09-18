from typing import Optional

from ..dao.post import AbstractPostDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import PostDTO, PostRequestDTO

class PostService:
    __slots__ = (
        "_common_dao",
        "_post_dao"
    )

    def __init__(
            self,
            post_dao: AbstractPostDAO,
            common_dao: AbstractCommonDAO
    ):
        self._post_dao = post_dao
        self._common_dao = common_dao

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

    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        result = await self._post_dao.get_unchecked_posts_from_user(sender_tg_id=sender_tg_id)
        return result

    async def get_unchecked_posts(self) -> list[PostDTO]:
        result = await self._post_dao.get_unchecked_posts()

        return result

    async def add_post(self, post: PostRequestDTO) -> PostDTO:
        result = await self._post_dao.add_post(post=post)
        await self._common_dao.commit()
        return result

    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO:
        result = await self._post_dao.update_post(post_id=post_id, post=post)
        await self._common_dao.commit()
        return result

    async def delete_post_by_user(self, post_id: int) -> bool:
        post = await self.get_post_by_id(post_id)

        if post.is_checked or post.is_paid:
            return False

        result = await self._post_dao.delete_post(post_id=post_id)
        await self._common_dao.commit()
        return result

    async def approve_post(self, post_id: int) -> None:
        post = await self.get_post_by_id(post_id)
        post.is_checked = True
        await self.update_post(post_id, post)
        await self._common_dao.commit()

    async def reject_post(self, post_id: int) -> None:
        result = await self.delete_post(post_id)
        await self._common_dao.commit()
        return result

    async def get_approved_posts(self) -> list[PostDTO]:
        return await self._post_dao.get_approved_posts()

    async def mark_as_published(self, post_id: int):
        await self._post_dao.mark_as_published(post_id)
        await self._common_dao.commit()

    async def get_unpaid_posts(self) -> list[PostDTO]:
        return await self._post_dao.get_unpaid_posts()

    async def mark_as_paid(self, post_id: int):
        await self._post_dao.mark_as_paid(post_id)
        await self._common_dao.commit()

    async def set_payment_id(self, post_id: int, payment_id: str):
        await self._post_dao.set_payment_id(post_id, payment_id)
        await self._common_dao.commit()
