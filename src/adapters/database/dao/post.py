from abc import ABC, abstractmethod
import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.dto import PostDTO, PostRequestDTO
from src.adapters.database.structures import Post, User


class AbstractPostDAO(ABC):
    @abstractmethod
    async def get_post(self, post_id: int | None = None, sender_id: int | None = None,
                       name: str | None = None) -> PostDTO | None:
        """
        Get post by id or sender_id and name
        :param post_id:
        :param sender_id:
        :param name:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_posts(self, sender_id: int, is_published: bool) -> list[PostDTO]:
        """
        Get posts by sender_id
        :param sender_id:
        :param is_published: bool
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        """
        Get unchecked posts from user
        :param sender_tg_id:
        :return: bool True if user has less than 3 unchecked posts
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unchecked_posts(self) -> list[PostDTO]:
        """
        Get all unchecked posts
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def add_post(self, post: PostRequestDTO) -> PostDTO | None:
        """
        Add post
        :param post: PostRequestDTO
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO | None:
        """
        Update post
        :param post_id:
        :param post: PostRequestDTO
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete_post(self, post_id: int) -> bool:
        """
        Delete post
        :param post_id:
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_approved_posts(self) -> list[PostDTO]:
        """
        Get all approved posts
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unpaid_posts(self) -> list[PostDTO]:
        """
        Get all unpaid posts
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_last_published_post_time(self, sender_id: int) -> datetime | None:
        """
        Get the time of the last published post by user
        :param sender_id: user id
        :return: datetime of last published post or None if no published posts
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_scheduled_posts_in_time_range(self, sender_id: int, start_time: datetime, end_time: datetime) -> list[
        PostDTO]:
        """
        Get scheduled posts in time range for user
        :param sender_id: user id
        :param start_time: start of time range
        :param end_time: end of time range
        :return: list of PostDTO
        """
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

    async def get_posts(self, sender_id: int, is_published: bool) -> list[PostDTO]:
        stmt = select(Post).where(
            Post.sender_id == sender_id,
            Post.is_published == is_published
        )
        result = await self._session.scalars(stmt)
        posts = result.all()

        return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
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

    async def get_unchecked_posts(self) -> list[PostDTO]:
        stmt = select(Post).where(
            Post.is_checked == False
        )
        result = await self._session.scalars(stmt)
        posts = result.all()
        return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

    async def add_post(self, post: PostRequestDTO) -> PostDTO | None:
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

    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO | None:
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
            .values(**post.model_dump(exclude_unset=True))
            .returning(Post)
        )
        result = await self._session.scalar(stmt)
        return PostDTO.model_validate(result, from_attributes=True)

    async def delete_post(self, post_id: int) -> bool:
        stmt = delete(Post).where(Post.id == post_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_approved_posts(self) -> list[PostDTO]:
        result = await self._session.scalars(
            select(Post)
            .where(Post.is_checked == True)
            .where(Post.is_paid == True)
            .where(Post.is_published == False)
        )
        posts = result.all()
        return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

    async def get_unpaid_posts(self) -> list[PostDTO]:
        result = await self._session.execute(
            select(Post)
            .where(Post.is_paid == False)
            .where(Post.payment_id.is_not(None))
        )
        posts = result.scalars().all()
        return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

    async def get_last_published_post_time(self, sender_id: int) -> datetime | None:
        stmt = select(Post.created_at).where(
            Post.sender_id == sender_id,
            Post.is_published == True
        ).order_by(Post.created_at.desc()).limit(1)

        result = await self._session.scalar(stmt)
        return result

    async def get_scheduled_posts_in_time_range(self, sender_id: int, start_time: datetime, end_time: datetime) -> list[
        PostDTO]:
        stmt = select(Post).where(
            Post.sender_id == sender_id,
            Post.publish_date >= start_time,
            Post.publish_date <= end_time,
            Post.is_published == False
        )

        result = await self._session.scalars(stmt)
        posts = result.all()
        return [PostDTO.model_validate(post, from_attributes=True) for post in posts]