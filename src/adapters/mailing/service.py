import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramAPIError
from redis.asyncio import Redis

from src.config.reader import Config
from src.adapters.database.dto import PostDTO

class Mailing:
    def __init__(self, bot: Bot, redis: Redis, config: Config):
        self._bot = bot
        self._redis = redis
        self._channel_chat_id = config.bot.channel_chat_id

    async def send_to_channel(self, post: PostDTO):
        try:
            text = f"{post.name}\n\n{post.text}" if post.name else post.text

            if post.media_type == 'photo' and post.media_link:
                await self._bot.send_photo(
                    chat_id=self._channel_chat_id,
                    photo=post.media_link,
                    caption=text
                )
            elif post.media_type == 'video' and post.media_link:
                await self._bot.send_video(
                    chat_id=self._channel_chat_id,
                    video=post.media_link,
                    caption=text
                )
            else:
                await self._bot.send_message(
                    chat_id=self._channel_chat_id,
                    text=text
                )
        except (TelegramBadRequest, TelegramForbiddenError, TelegramAPIError) as e:
            logging.error(f"Failed to send post {post.id} to channel: {e}")