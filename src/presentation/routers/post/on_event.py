from typing import Any
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from dishka.integrations.aiogram import FromDishka
from aiogram_dialog.widgets.kbd import Button

from src.adapters.database.service import UserService, PostService
from src.adapters.database.dto import UserRequestDTO, PostRequestDTO
from src.presentation.states import PostSG


@inject
async def start_create_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(InformationSG.add_post)


@inject
async def on_name_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.switch_to(PostSG.add_post_text)


@inject
async def on_text_entered(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        text: str
):
    dialog_manager.dialog_data["text"] = text
    await dialog_manager.switch_to(PostSG.add_post_image)


@inject
async def on_image_sent(
        message: Message,
        widget: Any,
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService]
):
    if message.photo:
        dialog_manager.dialog_data["image_link"] = message.photo[-1].file_id
    await finish_post_creation(dialog_manager, post_service, user_service)


@inject
async def on_skip_image(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService]
):
    dialog_manager.dialog_data["image_link"] = None
    await finish_post_creation(dialog_manager, post_service, user_service)


@inject
async def finish_post_creation(
        dialog_manager: DialogManager,
        post_service: FromDishka[PostService],
        user_service: FromDishka[UserService]
):
    user = await user_service.get_current_user()
    post_data = dialog_manager.dialog_data

    post = PostRequestDTO(
        name=post_data["name"],
        text=post_data["text"],
        image_link=post_data.get("image_link"),
        sender_id=user.id
    )

    try:
        created_post = await post_service.add_post(post)
        await dialog_manager.event.answer("Пост успешно создан!")
    except Exception as e:
        await dialog_manager.event.answer(f"Ошибка при создании поста: {str(e)}")

    await dialog_manager.done()