from abc import ABC, abstractmethod
import logging
from typing import Optional, List

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.database.dto import PostDTO, PostRequestDTO
from src.adapters.database.structures import Post


class AbstractPostDAO(ABC):
    @abstractmethod
    async def get_post(self, id: int | None = None, sender_id: int | None = None,
                       name: str | None = None) -> PostDTO | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_posts(self, sender_id: int) -> list[PostDTO]:
        raise NotImplementedError()

    @abstractmethod
    async def insert_post(self, post: PostRequestDTO) -> PostDTO:
        raise NotImplementedError()

    @abstractmethod
    async def update_post(self, post: PostRequestDTO) -> PostDTO:
        raise NotImplementedError()

    @abstractmethod
    async def delete_post(self, post_id: int) -> bool:
        raise NotImplementedError()


class PostDAO(AbstractPostDAO):
    __slots__ = ("_session", "_logger")

    def __init__(self, session: AsyncSession, logger: logging.Logger | None = None):
        self._session = session
        self._logger = logger or logging.getLogger(__name__)

    async def get_post(self, id: int | None = None, sender_id: int | None = None,
                       name: str | None = None) -> PostDTO | None:
        # Исправлено условие проверки параметров
        if not id and not (sender_id and name):
            raise ValueError("Either id or both sender_id and name must be passed")

        try:
            stmt = select(Post)
            if id:
                stmt = stmt.where(Post.id == id)
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
            stmt = select(Post).where(Post.sender_id == sender_id)
            result = await self._session.scalars(stmt)
            posts = result.all()

            return [PostDTO.model_validate(post, from_attributes=True) for post in posts]

        except SQLAlchemyError as e:
            self._logger.error(f"Database error in get_posts: {e}")
            raise

    async def insert_post(self, post: PostRequestDTO) -> PostDTO:
        try:
            # Проверяем, существует ли пост с таким же именем от этого отправителя
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

    async def update_post(self, post: PostRequestDTO) -> PostDTO:
        try:
            stmt = (
                update(Post)
                .where(Post.id == post.id)
                .values(**post.model_dump())
                .returning(Post)
            )
            result = await self._session.scalar(stmt)

            if not result:
                raise ValueError(f"Post with id {post.id} not found")

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