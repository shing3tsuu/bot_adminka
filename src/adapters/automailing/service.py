import asyncio
import datetime
from dishka import FromDishka, AsyncContainer
import logging
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.adapters.database.service import AbstractPostService
from src.adapters.mailing.service import Mailing


class AutoMailing:
    def __init__(self, mailing: Mailing, container: AsyncContainer):
        self._mailing = mailing
        self._container = container
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger(__name__)

    @inject
    async def check_posts(self):
        async with self._lock:
            try:
                async with self._container() as request_container:
                    post_service = await request_container.get(AbstractPostService)
                    posts = await post_service.get_approved_posts()

                    current_time = datetime.datetime.now()
                    published_users = set()  # Track users who had posts published in this cycle

                    self._logger.info(f"Checking {len(posts)} approved posts for publishing")

                    for post in posts:
                        # Skip if user already had a post published in this cycle
                        if post.sender_id in published_users:
                            self._logger.debug(
                                f"Skipping post {post.id} - user {post.sender_id} already published in this cycle")
                            continue

                        # Check if post should be published now
                        should_publish = False

                        if post.is_publish_now:
                            # For immediate posts, check 24h limit
                            can_publish, reason = await post_service.can_user_publish_now(post.sender_id)
                            if can_publish:
                                should_publish = True
                            else:
                                self._logger.debug(f"Post {post.id} cannot be published now: {reason}")
                        elif post.publish_date and post.publish_date <= current_time:
                            # For scheduled posts, check if it's time and 24h limit
                            can_publish, reason = await post_service.can_user_publish_now(post.sender_id)
                            if can_publish:
                                should_publish = True
                            else:
                                self._logger.debug(f"Scheduled post {post.id} cannot be published: {reason}")

                        if should_publish:
                            try:
                                self._logger.info(f"Publishing post {post.id} for user {post.sender_id}")
                                await self._mailing.send_to_channel(post)
                                await post_service.mark_as_published(post.id)
                                published_users.add(post.sender_id)  # Mark user as published in this cycle
                                self._logger.info(f"Successfully published post {post.id}")

                                # Небольшая задержка между публикациями
                                await asyncio.sleep(1)

                            except Exception as e:
                                self._logger.error(f"Failed to publish post {post.id}: {e}")

            except Exception as e:
                self._logger.error(f"Error in check_posts: {e}")

    async def start(self):
        self._logger.info("Starting AutoMailing service")
        while True:
            try:
                await self.check_posts()
            except Exception as e:
                self._logger.error(f"Error in AutoMailing main loop: {e}")
            await asyncio.sleep(60)