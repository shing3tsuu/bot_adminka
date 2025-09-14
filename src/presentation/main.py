import asyncio
import orjson
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs

from redis.asyncio import Redis

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka

from fastapi import FastAPI
import uvicorn
from src.presentation.routers.webhooks.yookassa import router as yookassa_router

from src.presentation.providers.app import AppProvider, MailingProvider
from src.config.reader import reader, Config

from src.presentation.routers.common import common_router

from src.adapters.mailing.service import Mailing
from src.adapters.automailing.service import AutoMailing

background_tasks = set()


async def run_bot():
    config = reader()

    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db
    )
    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
        json_loads=orjson.loads,
        json_dumps=orjson.dumps
    )

    bot = Bot(
        token=config.bot.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    await bot.delete_webhook(drop_pending_updates=True)

    container = make_async_container(
        AppProvider(),
        AiogramProvider(),
        context={Config: config}
    )

    mailing_container = make_async_container(
        MailingProvider(),
        context={
            Bot: bot,
            Redis: redis,
            Config: config,
        }
    )

    isolation = storage.create_isolation()

    dp = Dispatcher(events_isolation=isolation, storage=storage)

    dp.include_router(common_router)

    setup_dialogs(dp, events_isolation=isolation)
    setup_dishka(container=container, router=dp, auto_inject=True)

    dp.shutdown.register(container.close)

    mailing = Mailing(bot=bot, redis=redis, config=config)
    automailing = AutoMailing(mailing=mailing, container=container)

    try:
        # background_tasks.add(asyncio.create_task(automailing.start()))
        await automailing.start()
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()

async def run_webhook_server():
    """
    Need for yookassa webhooks response
    :return:
    """
    app = FastAPI()
    app.include_router(yookassa_router)

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    await asyncio.gather(
        run_bot(),
        run_webhook_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
