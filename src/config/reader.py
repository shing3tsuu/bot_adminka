from dataclasses import dataclass
from environs import Env
from typing import Optional

@dataclass
class BotConfig:
    bot_token: str | None = None
    admin_ids: list[int] | None = None

@dataclass
class DBConfig:
    # Postgresql
    host: str | None = None
    port: int | None = None
    name: str | None = None
    user: str | None = None
    password: str | None = None

    # Sqlite
    path: str | None = None

@dataclass
class RedisConfig:
    host: str | None = 'localhost'
    password: str | None = None
    port: int | None = 6379
    db: int | None = 0

@dataclass
class Config:
    bot: BotConfig
    db: DBConfig
    redis: RedisConfig

def reader() -> Config:
    env = Env()
    env.read_env(".env")

    return Config(
        bot=BotConfig(
            bot_token=env('BOT_TOKEN', None),
            admin_ids=[env.int('ADMIN_ID', None)]
        ),
        db=DBConfig(
            host=env('DB_HOST', None),
            port=env.int('DB_PORT', None),
            name=env('DB_NAME', None),
            user=env('DB_USER', None),
            password=env('DB_PASSWORD', None),
            path=env('DB_PATH', 'data/bot.db')
        ),
        redis=RedisConfig(
            host=env('REDIS_HOST', 'localhost'),
            password=env('REDIS_PASSWORD', None),
            port=env.int('REDIS_PORT', 6379),
            db=env.int('REDIS_DB', 0)
        )
    )