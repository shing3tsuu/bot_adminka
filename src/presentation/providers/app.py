from typing import AsyncIterable
from aiogram import Bot
from aiogram.types import TelegramObject
from redis.asyncio import Redis
from dishka import Provider, provide, Scope, from_context
from dishka import AsyncContainer, FromDishka
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.reader import Config
from src.adapters.database.dao import (
    AbstractUserDAO,
    UserDAO,
    AbstractCommonDAO,
    CommonDAO,
    AbstractPostDAO,
    PostDAO
)
from src.adapters.database.service import UserService, PostService
from src.adapters.database.structures import Base

from src.adapters.mailing.service import Mailing
from src.adapters.automailing.service import AutoMailing

class AppProvider(Provider):
    scope = Scope.APP
    config_provider = from_context(provides=Config)

    @staticmethod
    async def create_tables(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @provide(scope=Scope.APP)
    async def config(self, config: Config) -> async_sessionmaker:
        engine = create_async_engine(
            f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}",
            pool_size=50,
            pool_timeout=15,
            pool_recycle=1500,
            pool_pre_ping=True,
            max_overflow=15,
            connect_args={
                "server_settings": {"jit": "off"}
            },
            echo=True,
        )
        await self.create_tables(engine)
        return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def new_connection(self, sessionmaker: async_sessionmaker) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def user_dao(self, session: AsyncSession) -> AbstractUserDAO:
        return UserDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def post_dao(self, session: AsyncSession) -> AbstractPostDAO:
        return PostDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def common_dao(self, session: AsyncSession) -> AbstractCommonDAO:
        return CommonDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def user_service(
            self,
            obj: TelegramObject,
            user_dao: AbstractUserDAO,
            common_dao: AbstractCommonDAO,
    ) -> UserService:
        try:
            user_id = obj.from_user.id
        except AttributeError:
            user_id = -1
        return UserService(
            user_dao=user_dao,
            common_dao=common_dao,
            current_user_tg_id=user_id
        )

    @provide(scope=Scope.REQUEST)
    async def post_service(
            self,
            post_dao: AbstractPostDAO,
            common_dao: AbstractCommonDAO,
    ) -> PostService:
        return PostService(
            common_dao=common_dao,
            post_dao=post_dao
        )

class MailingProvider(Provider):
    @provide(scope=Scope.APP)
    async def mailing(self, bot: Bot, redis: Redis, config: Config) -> Mailing:
        return Mailing(bot=bot, redis=redis, channel_chat_id=config.bot.channel_chat_id)

    @provide(scope=Scope.APP)
    async def automailing(self, mailing: Mailing, container: AsyncContainer) -> AutoMailing:
        return AutoMailing(mailing=mailing, container=container)
