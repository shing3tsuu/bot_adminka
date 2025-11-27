import os
import asyncio
import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramAPIError
from redis.asyncio import Redis

from src.config.reader import Config
from src.adapters.database.dto import PostDTO


class Mailing:
    def __init__(self, bot: Bot, redis: Redis, config: Config):
        self._bot = bot
        self._redis = redis
        self._channel_chat_id = config.bot.channel_chat_id
        self._media_root = config.media.media_root

    async def send_to_channel(self, post: PostDTO):
        try:
            text = f"{post.name}\n\n{post.text}" if post.name else post.text

            if post.media_link:
                filename = os.path.basename(post.media_link)
                file_path = os.path.join(self._media_root, 'posts', filename)

                if post.media_type == 'photo':
                    await self._bot.send_photo(
                        chat_id=self._channel_chat_id,
                        photo=FSInputFile(file_path),
                        caption=text
                    )
                elif post.media_type == 'video':
                    await self._bot.send_video(
                        chat_id=self._channel_chat_id,
                        video=FSInputFile(file_path),
                        caption=text
                    )
            else:
                await self._bot.send_message(
                    chat_id=self._channel_chat_id,
                    text=text
                )
        except (TelegramBadRequest, TelegramForbiddenError, TelegramAPIError) as e:
            logging.error(f"Failed to send post {post.id} to channel: {e}")