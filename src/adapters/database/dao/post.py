from abc import ABC, abstractmethod
import logging
from typing import Optional, List

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.dto import PostDTO, PostRequestDTO
from src.adapters.database.structures import Post, User


class AbstractPostDAO(ABC):
    @abstractmethod
    async def get_post(self, post_id: int | None = None, sender_id: int | None = None,
                       name: str | None = None) -> PostDTO | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_posts(self, sender_id: int) -> list[PostDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def get_unchecked_posts(self) -> list[PostDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def add_post(self, post: PostRequestDTO) -> PostDTO:
        raise NotImplementedError()

    @abstractmethod
    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO:
        raise NotImplementedError()

    @abstractmethod
    async def delete_post(self, post_id: int) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def get_approved_posts(self) -> list[PostDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def mark_as_published(self, post_id: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get_unpaid_posts(self) -> list[PostDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def mark_as_paid(self, post_id: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def set_payment_id(self, post_id: int, payment_id: str) -> None:
        raise NotImplementedError()


class PostDAO(AbstractPostDAO):
    __slots__ = ("_session", "_logger")

    def __init__(self, session: AsyncSession, logger: logging.Logger | None = None):
        self._session = session
        self._logger = logger or logging.getLogger(__name__)

    async def get_post(self, post_id: int | None = None, sender_id: int | None = None,
                       name: str | None = None) -> PostDTO | None:
        if not post_id and not (sender_id and name):
            raise ValueError("Either id or both sender_id and name must be passed")

        try:
            stmt = select(Post)
            if post_id:
                stmt = stmt.where(Post.id == post_id)
            elif sender_id and name:
                stmt = stmt.where(
                    Post.sender_id == sender_id,
                    func.lower(Post.name) == func.lower(name)
                )

            result = await self._session.scalar(stmt)
            return PostDTO.model_validate(result, from_attributes=True) if result else None

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_post: {e}")
            raise

    async def get_posts(self, sender_id: int) -> list[PostDTO]:
        try:
            stmt = select(Post).where(
                Post.sender_id == sender_id
            )
            result = await self._session.scalars(stmt)
            posts = result.all()

            return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_posts: {e}")
            raise

    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        try:
            user_stmt = select(User).where(User.tg_id == sender_tg_id)
            user_result = await self._session.scalar(user_stmt)

            if not user_result:
                return True

            stmt = select(func.count(Post.id)).where(
                Post.sender_id == user_result.id,
                Post.is_checked == False
            )
            count = await self._session.scalar(stmt)

            return count < 3

        except SQLAlchemyError as e:
            self._logger.error("Database error in get_unchecked_posts_from_user: %s", e)
            return True


    async def get_unchecked_posts(self) -> list[PostDTO]:
        try:
            stmt = select(Post).where(
                Post.is_checked == False
            )
            result = await self._session.scalars(stmt)
            posts = result.all()

            return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

        except SQLAlchemyError as e:
            self._logger.error("Database error in get_unchecked_posts: %s",e)
            raise

    async def add_post(self, post: PostRequestDTO) -> PostDTO:
        try:
            existing_post = await self._session.scalar(
                select(Post).where(
                    Post.sender_id == post.sender_id,
                    func.lower(Post.name) == func.lower(post.name)
                )
            )

            if existing_post:
                raise ValueError("Post with this name already exists for this sender")

            stmt = (
                insert(Post)
                .values(**post.model_dump())
                .returning(Post)
            )
            result = await self._session.scalar(stmt)
            return PostDTO.model_validate(result, from_attributes=True)

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in insert_post: {e}")
            raise

    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO:
        try:
            ex_post = await self._session.scalar(
                select(Post).where(
                    Post.id == post_id
                )
            )

            if not ex_post:
                raise ValueError(f"Post with id {post_id} not found")

            stmt = (
                update(Post)
                .where(Post.id == post_id)
                .values(**post.model_dump())
                .returning(Post)
            )
            result = await self._session.scalar(stmt)

            return PostDTO.model_validate(result, from_attributes=True)

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in update_post: {e}")
            raise

    async def delete_post(self, post_id: int) -> bool:
        try:
            stmt = delete(Post).where(Post.id == post_id)
            result = await self._session.execute(stmt)
            return result.rowcount > 0

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in delete_post: {e}")
            raise

    async def get_approved_posts(self) -> list[PostDTO]:
        try:
            result = await self._session.scalars(
                select(Post)
                .where(Post.is_checked == True)
                .where(Post.is_paid == True)
                .where(Post.is_published == False)
            )
            posts = result.all()
            return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

        except SQLAlchemyError as e:
            self._logger.error("Database error in get_approved_posts: %s",e)
            return []

    async def mark_as_published(self, post_id: int) -> None:
        try:
            await self._session.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(is_published=True)
            )

        except SQLAlchemyError as e:
            self._logger.error("Database error in mark_as_published: %s",e)
            raise

    async def get_unpaid_posts(self) -> list[PostDTO]:
        try:
            result = await self._session.execute(
                select(Post)
                .where(Post.is_paid == False)
                .where(Post.payment_id.is_not(None))
            )
            posts = result.scalars().all()
            return [PostDTO.model_validate(post, from_attributes=True) for post in posts]
        except SQLAlchemyError as e:
            self._logger.error("Database error in get_unpaid_posts: %s", e)
            return []

    async def mark_as_paid(self, post_id: int) -> None:
        try:
            await self._session.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(is_paid=True)
            )
        except SQLAlchemyError as e:
            self._logger.error("Database error in mark_as_paid: %s", e)
            raise

    async def set_payment_id(self, post_id: int, payment_id: str) -> None:
        try:
            await self._session.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(payment_id=payment_id)
            )
        except SQLAlchemyError as e:
            self._logger.error("Database error in set_payment_id: %s", e)
            raise

