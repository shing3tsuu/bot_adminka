import os
import uuid
import aiofiles
import re
from pathlib import Path
from typing import Any
from datetime import datetime, date, time
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from dishka.integrations.aiogram import FromDishka
from aiogram_dialog.widgets.kbd import Button, Calendar
from aiogram_dialog import StartMode

from src.adapters.database.service import UserService, PostService
from src.adapters.database.dto import PostRequestDTO
from src.presentation.states import PostSG, MenuSG
from src.config.reader import Config

# Banned words list (add more if needed)
BANNED_WORDS = ["мат", "брань", "оскорбление"]

def contains_banned_words(text: str) -> list:
    """
    Function to check if the text contains any of the banned words.
    :param text:
    :return:
    """
    found_words = []
    for word in BANNED_WORDS:
        if word in text.lower():
            found_words.append(word)
    return found_words

async def save_media(
        media_file: bytes,
        media_type: str,
        media_config: Any  # Принимаем MediaConfig вместо Config
) -> str:
    """
    Function to save media file. Uses config.media_url to generate relative path.
    :param media_file:
    :param media_type:
    :param media_config:
    :return:
    """
    # Create directory if not exists
    media_root = Path(media_config.media_root)
    posts_dir = media_root / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = media_type.split('/')[-1] if '/' in media_type else "jpg"
    filename = f"{uuid.uuid4()}.{file_extension}"
    filepath = posts_dir / filename

    # Save media file
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(media_file)

    # Return relative path
    relative_path = f"posts/{filename}"
    return f"{media_config.media_url}{relative_path}"

def validate_time(time_str: str) -> bool:
    """
    Function to validate time format.
    :param time_str:
    :return:
    """
    pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    return bool(pattern.match(time_str))

@inject
async def back_to_main(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(MenuSG.menu, mode=StartMode.RESET_STACK)

@inject
async def start_create_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(PostSG.add_post)

@inject
async def on_name_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    if len(text) < 2 or len(text) > 100:
        await message.answer("Название должно содержать от 2 до 100 символов.")
        return

    dialog_manager.dialog_data["name"] = text
    await dialog_manager.switch_to(PostSG.add_post_text)

@inject
async def on_text_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    """
    Function to validate text length and check for banned words.
    :param message:
    :param widget:
    :param dialog_manager:
    :param text:
    :return:
    """
    if len(text) < 2 or len(text) > 1000:
        await message.answer("Текст должен содержать от 2 до 1000 символов.")
        return

    banned_words = contains_banned_words(text)
    if banned_words:
        dialog_manager.dialog_data["text"] = text
        dialog_manager.dialog_data["banned_words"] = ", ".join(banned_words)
        await dialog_manager.switch_to(PostSG.moderation_warning)
        return

    dialog_manager.dialog_data["text"] = text
    await dialog_manager.switch_to(PostSG.add_post_media)


@inject
async def on_media_sent(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        config: FromDishka[Config]
):
    """
    Function to handle media upload. Checks file size and media type.
    :param message:
    :param widget:
    :param dialog_manager:
    :param config:
    :return:
    """
    media_url = None
    media_type = "photo"  # По умолчанию считаем, что это фото

    try:
        if message.photo:
            photo = message.photo[-1]
            media_type = "photo"

            # Check file size
            if photo.file_size > config.media.max_file_size:
                await message.answer(
                    f"Файл слишком большой. Максимальный размер: {config.media.max_file_size // 1024 // 1024}MB")
                return

            media_file = await message.bot.download(photo)
            media_url = await save_media(media_file.read(), "image/jpeg", config.media)

        elif message.video:
            media_type = "video"
            if message.video.file_size > config.media.max_file_size:
                await message.answer(
                    f"Файл слишком большой. Максимальный размер: {config.media.max_file_size // 1024 // 1024}MB")
                return

            video = message.video
            media_file = await message.bot.download(video)
            media_url = await save_media(media_file.read(), video.mime_type, config.media)

        elif message.document:
            # Определяем тип документа по MIME-type
            if message.document.mime_type.startswith('image/'):
                media_type = "photo"
            elif message.document.mime_type.startswith('video/'):
                media_type = "video"
            else:
                await message.answer("Поддерживаются только изображения и видео")
                return

            if message.document.file_size > config.media.max_file_size:
                await message.answer(
                    f"Файл слишком большой. Максимальный размер: {config.media.max_file_size // 1024 // 1024}MB")
                return

            document = message.document
            media_file = await message.bot.download(document)
            media_url = await save_media(await media_file.read(), document.mime_type, config.media)

    except Exception as e:
        await message.answer(f"Ошибка при загрузке файла: {str(e)}")
        return

    dialog_manager.dialog_data["media_url"] = media_url
    dialog_manager.dialog_data["media_type"] = media_type  # Сохраняем тип медиа
    await dialog_manager.switch_to(PostSG.preview)

@inject
async def on_skip_media(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    dialog_manager.dialog_data["media_url"] = None
    dialog_manager.dialog_data["media_type"] = None
    await dialog_manager.switch_to(PostSG.preview)

@inject
async def on_confirm_preview(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(PostSG.confirm_publish)

@inject
async def on_edit_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(PostSG.add_post)

@inject
async def on_edit_text(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    # Возвращаемся к редактированию текста
    await dialog_manager.switch_to(PostSG.add_post_text)

@inject
async def on_publish_now(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService]
):
    """
    Function to publish the post immediately (after moderation).
    :param callback:
    :param button:
    :param dialog_manager:
    :param post_service:
    :param user_service:
    :return:
    """
    user = await user_service.get_current_user()
    post_data = dialog_manager.dialog_data

    post = PostRequestDTO(
        name=post_data["name"],
        text=post_data["text"],
        media_link=post_data.get("media_url"),
        media_type=post_data.get("media_type", "photo"),  # Добавляем тип медиа
        is_publish_now=True,
        publish_date=None,
        is_checked=False,
        is_paid=False,
        sender_id=user.id
    )

    try:
        created_post = await post_service.add_post(post)
        await callback.message.answer("Пост опубликован!")
    except Exception as e:
        await callback.message.answer(f"Ошибка при публикации поста: {str(e)}")

    await dialog_manager.done()


@inject
async def on_schedule_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(PostSG.schedule_date)

@inject
async def on_date_selected(
        callback: CallbackQuery,
        widget: Calendar,
        dialog_manager: DialogManager,
        selected_date: date
):
    dialog_manager.dialog_data["scheduled_date"] = selected_date.isoformat()
    await dialog_manager.switch_to(PostSG.schedule_time)


@inject
async def on_time_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService]
):
    """
    Function to schedule the post.
    Get scheduled date from dialog data
    :param message:
    :param widget:
    :param dialog_manager:
    :param text:
    :param post_service:
    :param user_service:
    :return:
    """
    # Check time format
    if not validate_time(text):
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 13:00)")
        return

    # Get scheduled date from dialog data
    scheduled_date_str = dialog_manager.dialog_data.get("scheduled_date")
    if not scheduled_date_str:
        await message.answer("Ошибка: дата не выбрана.")
        return

    # Create datetime object
    scheduled_date = date.fromisoformat(scheduled_date_str)
    hours, minutes = map(int, text.split(':'))
    scheduled_time = time(hours, minutes)
    scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)

    if scheduled_datetime < datetime.now():
        await message.answer("Нельзя запланировать публикацию в прошлом. Выберите другое время.")
        return

    user = await user_service.get_current_user()
    post_data = dialog_manager.dialog_data

    post = PostRequestDTO(
        name=post_data["name"],
        text=post_data["text"],
        media_link=post_data.get("media_url"),
        media_type=post_data.get("media_type", "photo"),
        is_publish_now=False,
        publish_date=scheduled_datetime,
        is_checked=False,
        is_paid=False,
        sender_id=user.id
    )

    try:
        created_post = await post_service.add_post(post)
        await message.answer(f"Пост запланирован на {scheduled_datetime.strftime('%d.%m.%Y %H:%M')}!")
    except Exception as e:
        await message.answer(f"Ошибка при планировании поста: {str(e)}")

    await dialog_manager.done()
