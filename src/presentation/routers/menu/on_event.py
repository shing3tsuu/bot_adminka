from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject
from dishka.integrations.aiogram import FromDishka
from aiogram_dialog.widgets.kbd import Button

from src.presentation.states import PostSG, MyPostsSG
from src.adapters.database.service import UserService

@inject
async def start_create_post(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(PostSG.add_post)

@inject
async def show_my_posts(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.start(MyPostsSG.list)

@inject
async def show_info(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    """
    Shows information about the bot (can be changed)
    :param callback:
    :param button:
    :param dialog_manager:
    :return:
    """
    info_text = (
        "ℹ️ Информация о боте:\n\n"
        "Этот бот позволяет создавать и публиковать посты. "
        "Для начала работы нажмите 'Создать пост' и следуйте инструкциям."
    )

    await callback.message.answer(info_text)