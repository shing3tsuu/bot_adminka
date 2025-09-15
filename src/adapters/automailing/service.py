import asyncio
import datetime
from dishka import FromDishka, AsyncContainer
import logging
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.adapters.database.service import PostService
from src.adapters.mailing.service import Mailing

from src.adapters.payment.checker import PaymentChecker


class AutoMailing:
    def __init__(self, mailing: Mailing, payment_checker: PaymentChecker, container: AsyncContainer):
        self._mailing = mailing
        self._payment_checker = payment_checker
        self._container = container

    @inject
    async def check_posts(self):
        async with self._container() as request_container:
            post_service = await request_container.get(PostService)
            posts = await post_service.get_approved_posts()

            current_time = datetime.datetime.now()
            if posts:
                for post in posts:
                    if post.publish_date is None or post.publish_date <= current_time:
                        await self._mailing.send_to_channel(post)
                        await post_service.mark_as_published(post.id)

    async def start(self):
        while True:
            await self._payment_checker.check_payments()
            await asyncio.sleep(10)
            await self.check_posts()
            await asyncio.sleep(50)
