import asyncio
import logging
from yookassa import Payment
from dishka import AsyncContainer
from src.adapters.database.service import PostService


class PaymentChecker:
    def __init__(self, container: AsyncContainer):
        self._container = container

    async def check_payments(self):
        async with self._container() as request_container:
            post_service = await request_container.get(PostService)
            unpaid_posts = await post_service.get_unpaid_posts()

            for post in unpaid_posts:
                if not post.payment_id:
                    continue

                try:
                    payment = Payment.find_one(post.payment_id)
                    if payment.status == 'succeeded':
                        await post_service.mark_as_paid(post.id)
                        logging.info(f"Payment for post {post.id} succeeded")
                except Exception as e:
                    logging.error(f"Error checking payment {post.payment_id}: {e}")