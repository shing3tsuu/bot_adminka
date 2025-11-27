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
    PostDAO,
    AbstractPriceDAO,
    PriceDAO
)
from src.adapters.database.service import (
    UserService, AbstractUserService,
    PostService, AbstractPostService,
    PriceService, AbstractPriceService
)
from src.adapters.database.structures import Base

from src.adapters.mailing.service import Mailing
from src.adapters.automailing.service import AutoMailing
from src.adapters.payment.checker import PaymentChecker

class AppProvider(Provider):
    scope = Scope.APP
    config_provider = from_context(provides=Config)

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
        )
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
    async def price_dao(self, session: AsyncSession) -> AbstractPriceDAO:
        return PriceDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def common_dao(self, session: AsyncSession) -> AbstractCommonDAO:
        return CommonDAO(session=session)

    @provide(scope=Scope.REQUEST)
    async def user_service(
            self,
            obj: TelegramObject,
            user_dao: AbstractUserDAO,
            common_dao: AbstractCommonDAO,
    ) -> AbstractUserService:
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
    ) -> AbstractPostService:
        return PostService(
            common_dao=common_dao,
            post_dao=post_dao
        )

    @provide(scope=Scope.REQUEST)
    async def price_service(
            self,
            price_dao: AbstractPriceDAO,
            common_dao: AbstractCommonDAO,
    ) -> AbstractPriceService:
        return PriceService(
            common_dao=common_dao,
            price_dao=price_dao
        )

class MailingProvider(Provider):
    @provide(scope=Scope.APP)
    async def mailing(self, bot: Bot, redis: Redis, config: Config) -> Mailing:
        return Mailing(bot=bot, redis=redis, channel_chat_id=config.bot.channel_chat_id)

    @provide(scope=Scope.APP)
    async def auto_mailing(self, mailing: Mailing, container: AsyncContainer) -> AutoMailing:
        return AutoMailing(mailing=mailing, container=container)

    @provide(scope=Scope.APP)
    async def payment_checker(self, container: AsyncContainer) -> PaymentChecker:
        return PaymentChecker(container=container)