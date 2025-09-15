Бот для публикации постов в Telegram-канале

Этот проект представляет собой Telegram-бота с системой модерации и оплаты для публикации контента в канале.
Основной функционал
Для пользователей

1.Регистрация с указанием ФИО и контактных данных

2.Создание постов с текстом и медиафайлами (фото/видео)

3.Планирование публикации (немедленно или в указанное время)

4.Просмотр своих постов и управление ими

5.Оплата постов через интеграцию с YooKassa

6.Удаление постов до момента модерации

Для администраторов

1.Модерация контента - одобрение или отклонение постов

2.Просмотр непроверенных постов

3.Управление опубликованным контентом

3.Отслеживание оплаченных постов

Технические особенности

1.Асинхронная архитектура на aiogram 3.x

2.Работа с PostgreSQL через SQLAlchemy 2.x

3.Интеграция с платежной системой YooKassa

4.Кэширование и FSM через Redis

5.Dependency Injection через Dishka

6.Поддержка медиафайлов с валидацией размера

7.Автоматическая публикация одобренных постов

Установка и запуск

    Клонируйте репозиторий

    Установите зависимости: pip install -r requirements.txt

    Настройте переменные окружения в файле .env (см. пример ниже)

    Запустите бота: python main.py

Конфигурация

Пример файла .env:

    BOT_TOKEN=your_bot_token
    BOT_URL=your_bot_url
    ADMIN_IDS=123456789
    CHANNEL_CHAT_ID=your_channel_chat_id

    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password

    REDIS_HOST=localhost
    REDIS_PASSWORD=your_redis_password
    REDIS_PORT=6379
    REDIS_DB=0

    MEDIA_ROOT=media
    MEDIA_URL=/media/
    MAX_FILE_SIZE=10485760

    YOOKASSA_SHOP_ID=your_shop_id
    YOOKASSA_SECRET_KEY=your_secret_key
    POST_PRICE=100.00

Структура проекта

    src/adapters/database/ - работа с базой данных (DAO, DTO, сервисы)

    src/adapters/mailing/ - функционал отправки сообщений в канал

    src/adapters/payment/ - интеграция с платежной системой

    src/config/ - конфигурация приложения

    src/presentation/ - презентационный слой (диалоги, роутеры)

    main.py - точка входа в приложение

Основные технологии

    Aiogram 3.x - фреймворк для Telegram ботов

    SQLAlchemy 2.x - ORM для работы с PostgreSQL

    Dishka - dependency injection контейнер

    YooKassa - платежная система

    Redis - кэширование и хранение состояний

    Pydantic - валидация данных
