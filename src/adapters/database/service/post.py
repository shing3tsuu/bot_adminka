from typing import Optional, List
import logging
from datetime import datetime, timedelta

from ..dao.post import AbstractPostDAO
from ..dao.common import AbstractCommonDAO
from src.adapters.database.dto import PostDTO, PostRequestDTO

from abc import ABC, abstractmethod

class AbstractPostService(ABC):
    @abstractmethod
    async def get_post_by_id(self, post_id: int) -> PostDTO | None:
        """
        Get post by id
        :param post_id:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_post_by_name(self, sender_id: int, name: str) -> PostDTO | None:
        """
        Get post by sender_id and name
        :param sender_id:
        :param name:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unpublished_posts(self, sender_id: int) -> list[PostDTO]:
        """
        Get unpublished posts by sender_id
        :param sender_id:
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        """
        Check if user has less than 3 unchecked posts
        :param sender_tg_id:
        :return: bool
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
    async def approve_post(self, post_id: int) -> PostDTO | None:
        """
        Approve post
        :param post_id:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def reject_post(self, post_id: int) -> bool:
        """
        Reject post
        :param post_id:
        :return: bool
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_approved_posts(self) -> list[PostDTO]:
        """
        Get approved posts
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def mark_as_published(self, post_id: int) -> PostDTO | None:
        """
        Mark post as published
        :param post_id:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_unpaid_posts(self) -> list[PostDTO]:
        """
        Get unpaid posts
        :return: list[PostDTO]
        """
        raise NotImplementedError()

    @abstractmethod
    async def mark_as_paid(self, post_id: int) -> PostDTO | None:
        """
        Mark post as paid
        :param post_id:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def set_payment_id(self, post_id: int, payment_id: str) -> PostDTO | None:
        """
        Set payment id for post
        :param post_id:
        :param payment_id:
        :return: PostDTO | None
        """
        raise NotImplementedError()

    @abstractmethod
    async def can_user_publish_now(self, sender_id: int) -> tuple[bool, str]:
        """
        Check if user can publish post now (24h limit)
        :param sender_id: user id
        :return: (can_publish, reason_message)
        """
        raise NotImplementedError()

    @abstractmethod
    async def can_schedule_post(self, sender_id: int, publish_time: datetime) -> tuple[bool, str]:
        """
        Check if user can schedule post at specified time (24h interval)
        :param sender_id: user id
        :param publish_time: desired publish time
        :return: (can_schedule, reason_message)
        """
        raise NotImplementedError()

class PostService(AbstractPostService):
    __slots__ = (
        "_common_dao",
        "_post_dao",
        "_logger"
    )

    def __init__(
            self,
            post_dao: AbstractPostDAO,
            common_dao: AbstractCommonDAO
    ):
        self._post_dao = post_dao
        self._common_dao = common_dao
        self._logger = logging.getLogger(__name__)

    async def get_post_by_id(self, post_id: int) -> PostDTO | None:
        try:
            result = await self._post_dao.get_post(post_id=post_id, sender_id=None, name=None)
            return result
        except Exception as e:
            self._logger.error("Error getting post by id %s in database: %s", post_id, e, exc_info=True)
            return None

    async def get_post_by_name(self, sender_id: int, name: str) -> PostDTO | None:
        try:
            result = await self._post_dao.get_post(post_id=None, sender_id=sender_id, name=name)
            return result
        except Exception as e:
            self._logger.error("Error getting post by sender_id %s and name %s in database: %s", sender_id, name, e, exc_info=True)
            return None

    async def get_unpublished_posts(self, sender_id: int) -> list[PostDTO]:
        try:
            result = await self._post_dao.get_posts(sender_id=sender_id, is_published=False)
            return result
        except Exception as e:
            self._logger.error("Error getting posts for sender_id %s in database: %s", sender_id, e, exc_info=True)
            return []

    async def get_published_posts(self, sender_id: int) -> list[PostDTO]:
        try:
            result = await self._post_dao.get_posts(sender_id=sender_id, is_published=True)
            return result
        except Exception as e:
            self._logger.error("Error getting posts for sender_id %s in database: %s", sender_id, e, exc_info=True)
            return []

    async def get_unchecked_posts_from_user(self, sender_tg_id: int) -> bool:
        try:
            result = await self._post_dao.get_unchecked_posts_from_user(sender_tg_id=sender_tg_id)
            return result
        except Exception as e:
            self._logger.error("Error getting unchecked posts from user %s in database: %s", sender_tg_id, e, exc_info=True)
            return False

    async def get_unchecked_posts(self) -> list[PostDTO]:
        try:
            result = await self._post_dao.get_unchecked_posts()
            return result
        except Exception as e:
            self._logger.error("Error getting unchecked posts in database: %s", e, exc_info=True)
            return []

    async def add_post(self, post: PostRequestDTO) -> PostDTO | None:
        try:
            result = await self._post_dao.add_post(post=post)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error adding post in database: %s", e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def update_post(self, post_id: int, post: PostRequestDTO) -> PostDTO | None:
        try:
            result = await self._post_dao.update_post(post_id=post_id, post=post)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error updating post %s in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def delete_post(self, post_id: int) -> bool:
        try:
            post = await self.get_post_by_id(post_id)
            if not post:
                return False
            if post.is_checked or post.is_paid:
                return False
            result = await self._post_dao.delete_post(post_id=post_id)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error deleting post %s in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return False

    async def approve_post(self, post_id: int) -> PostDTO | None:
        try:
            post = await self.get_post_by_id(post_id)
            if not post:
                return
            post.is_checked = True
            result = await self.update_post(post_id, post)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error approving post %s in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def reject_post(self, post_id: int) -> bool:
        try:
            result = await self.delete_post(post_id)
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error rejecting post %s in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return False

    async def get_approved_posts(self) -> list[PostDTO]:
        try:
            return await self._post_dao.get_approved_posts()
        except Exception as e:
            self._logger.error("Error getting approved posts in database: %s", e, exc_info=True)
            return []

    async def mark_as_published(self, post_id: int) -> PostDTO | None:
        try:
            result = await self._post_dao.update_post(
                post_id=post_id,
                post=PostRequestDTO(is_published=True),
            )
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error marking post %s as published in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def get_unpaid_posts(self) -> list[PostDTO]:
        try:
            return await self._post_dao.get_unpaid_posts()
        except Exception as e:
            self._logger.error("Error getting unpaid posts in database: %s", e, exc_info=True)
            return []

    async def mark_as_paid(self, post_id: int) -> PostDTO | None:
        try:
            result = await self._post_dao.update_post(
                post_id=post_id,
                post=PostRequestDTO(is_paid=True),
            )
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error marking post %s as paid in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def set_payment_id(self, post_id: int, payment_id: str) -> PostDTO | None:
        try:
            result = await self._post_dao.update_post(
                post_id=post_id,
                post=PostRequestDTO(payment_id=payment_id)
            )
            await self._common_dao.commit()
            return result
        except Exception as e:
            self._logger.error("Error setting payment_id for post %s in database: %s", post_id, e, exc_info=True)
            await self._common_dao.rollback()
            return None

    async def can_user_publish_now(self, sender_id: int) -> tuple[bool, str]:
        try:
            last_published = await self._post_dao.get_last_published_post_time(sender_id)

            if not last_published:
                return True, "Можно публиковать"

            time_since_last = datetime.now() - last_published
            hours_since_last = time_since_last.total_seconds() / 3600

            if hours_since_last < 24:
                hours_left = 24 - hours_since_last
                return False, f"Нельзя публиковать чаще чем раз в 24 часа. Следующий пост можно опубликовать через {hours_left:.1f} часов."

            return True, "Можно публиковать"

        except Exception as e:
            self._logger.error("Error checking publish limit for user %s: %s", sender_id, e, exc_info=True)
            return False, "Ошибка проверки ограничений публикации"

    async def can_schedule_post(self, sender_id: int, publish_time: datetime) -> tuple[bool, str]:
        try:
            # Check if publish_time is in the future
            if publish_time <= datetime.now():
                return False, "Время публикации должно быть в будущем"

            # Check 24h limit from last published post
            last_published = await self._post_dao.get_last_published_post_time(sender_id)
            if last_published:
                time_since_last = publish_time - last_published
                hours_since_last = time_since_last.total_seconds() / 3600

                if hours_since_last < 24:
                    hours_left = 24 - hours_since_last
                    return False, f"Нельзя публиковать чаще чем раз в 24 часа. Следующий пост можно опубликовать через {hours_left:.1f} часов после последней публикации."

            # Check for conflicts with other scheduled posts
            time_range_start = publish_time - timedelta(hours=24)
            time_range_end = publish_time + timedelta(hours=24)

            conflicting_posts = await self._post_dao.get_scheduled_posts_in_time_range(
                sender_id, time_range_start, time_range_end
            )

            # Filter out the current post being edited if any
            conflicting_posts = [p for p in conflicting_posts if p.publish_date != publish_time]

            if conflicting_posts:
                return False, "У вас уже есть запланированные посты в пределах 24 часов от выбранного времени. Выберите другое время."

            return True, "Можно запланировать публикацию"

        except Exception as e:
            self._logger.error("Error checking schedule limit for user %s: %s", sender_id, e, exc_info=True)
            return False, "Ошибка проверки ограничений планирования"