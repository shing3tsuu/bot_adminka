import asyncio
import datetime
from dishka import FromDishka, AsyncContainer
import logging
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.adapters.database.service import PostService
from src.adapters.mailing.service import Mailing


class AutoMailing:
    def __init__(self, mailing: Mailing, container: AsyncContainer):
        self._mailing = mailing
        self._container = container

    @inject
    async def check_posts(self):
        async with self._container() as request_container:
            post_service = await request_container.get(PostService)
            posts = await post_service.get_approved_posts()

            current_time = datetime.datetime.now()
            if posts:
                for post in posts:
                    if post.is_publish_now is True or post.publish_date <= current_time:
                        await self._mailing.send_to_channel(post)
                        await post_service.mark_as_published(post.id)

    async def start(self):
        while True:
            await self.check_posts()
            await asyncio.sleep(60)


